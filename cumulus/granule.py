
import os
import re
import logging
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
import cumulus.s3 as s3
from cumulus.loggers import getLogger
from cumulus.cli import cli
from cumulus.aws import run, activity

logger = getLogger(__name__)


class Granule(object):
    """ Class representing a data granule on S3 and processing that granule """

    # internally used keys
    inputs = {
        'in1': r'^.*-1.txt$',
        'in2': r'^.*-2.txt'
    }

    outputs = {
        'out1': r'^.*-1.txt$',
        'out2': r'^.*-2.txt$',
        'meta': r'^.*.xml$'
    }

    autocheck = True

    def __init__(self, filenames, gid=None, collection='granule', path='', s3path='', visibility={}, **kwargs):
        """ Initialize a new granule with filenames """
        self.collection = collection

        self.path = path
        self.s3path = s3path
        self.visibility = visibility

        self.local_in = {}
        self.local_out = []
        self.remote_out = []

        # determine which file is which type of input through use of regular expression
        self.remote_in = {}
        for f in filenames:
            self.add_input_file(f)

        # if gid not provided get common prefix
        if gid is not None:
            self.gid = gid
        else:
            self.gid = self._gid()

        # let child data granules determine if it's not enough
        if self.autocheck:
            totalfiles = len(self.remote_in) + len(self.local_in)
            if (len(self.inputs) != totalfiles) or (len(self.inputs) != len(filenames)):
                raise IOError('Files do not make up complete granule or extra files provided')

        extra = {
            'collectionName': self.collection,
            'granuleId': self.gid
        }
        self.logger = logging.LoggerAdapter(logger, extra)

    def _gid(self):
        gid = os.path.commonprefix([os.path.basename(f) for f in self.input_files])
        if gid == '':
            raise ValueError('Unable to determine granule ID from files, provide manually')
        return gid

    @property
    def input_files(self):
        """ Get dictionary of all input files, local or remote (prefers local first) """
        fnames = {k: v for k, v in self.local_in.items()}
        for k, v in self.remote_in.items():
            if k not in fnames:
                fnames[k] = v
        return fnames

    def add_input_file(self, filename):
        """ Adds an input file """
        for f in self.inputs:
            m = re.match(self.inputs[f], os.path.basename(filename))
            if m is not None:
                # does the file exist locally
                if os.path.exists(f):
                    self.local_in[f] = filename
                else:
                    self.remote_in[f] = filename

    def publish(self, protected_url='http://cumulus.com'):
        """ Return URLs for output granule(s), defaults to all public """
        urls = []
        for gran in self.local_out:
            granout = {}
            for key, fname in gran.items():
                s3obj = self.s3path.replace('s3://', '').split('/')
                vis = self.visibility.get(key, 'public')
                if vis == 'public':
                    public = 'http://%s.s3.amazonaws.com' % s3obj[0]
                    if len(s3obj) > 1:
                        for d in s3obj[1:]:
                            public = os.path.join(public, d)
                    granout[key] = os.path.join(public, os.path.basename(fname))
                elif vis == 'protected':
                    granout[key] = os.path.join(protected_url, os.path.basename(fname))
            urls.append(granout)
        return urls

    def download(self, key=None):
        """ Download input file from S3 """
        keys = self.inputs.keys() if key is None else [key]
        downloaded = []
        for key in keys:
            uri = self.remote_in[key]
            self.logger.info('downloading input file %s' % uri)
            fname = s3.download(uri, path=self.path)
            self.local_in[key] = fname
            downloaded.append(str(fname))
        return downloaded

    def upload(self):
        """ Upload local output files to S3 """
        self.logger.info('uploading output granules to %s' % self.s3path)
        for granule in self.local_out:
            if len(granule) < len(self.outputs):
                self.logger.warning("Not all output files were available for upload")
            remote = {}
            for f in granule:
                fname = granule[f]
                try:
                    uri = s3.upload(fname, self.s3path)
                    remote[f] = uri
                except Exception as e:
                    self.logger.error("Error uploading file %s: %s" % (os.path.basename(fname), str(e)))
            self.remote_out.append(remote)
        return [files.values() for files in self.remote_out]

    @classmethod
    def write_metadata(cls, meta, fout, pretty=False):
        """ Write metadata dictionary as XML file """
        # for lists, use the singular version of the parent XML name
        singular_key_func = lambda x: x[:-1]
        # convert to XML
        xml = dicttoxml(meta, custom_root='Granule', attr_type=False, item_func=singular_key_func)
        # The <Point> XML tag does not follow the same rule as singular
        # of parent since the parent in CMR is <Boundary>. Create metadata
        # with the <Points> parent, and this removes that tag
        xml = xml.replace('<Points>', '').replace('</Points>', '')
        # pretty print
        if pretty:
            dom = parseString(xml)
            xml = dom.toprettyxml()
        with open(fout, 'w') as f:
            f.write(xml)

    def clean(self):
        """ Remove input and output files """
        self.logger.info('Cleaning local files')
        for f in self.local_in.values():
            if os.path.exists(f):
                os.remove(f)
        for gran in self.local_out:
            for f in gran.values():
                if os.path.exists(f):
                    os.remove(f)

    def run(self, noclean=False):
        """ Run all steps and log: process, upload """
        try:
            self.logger.info('begin processing')
            self.process()
            self.upload()
            if noclean is False:
                self.clean()
            self.logger.info('processing completed')
        except Exception as e:
            self.logger.error({'message': 'Run error with granule', 'error': str(e)})
            raise e

    @classmethod
    def add_parser_args(cls, parser):
        """ Add class specific arguments to the parser """
        return parser

    @classmethod
    def cli(cls):
        cli(cls)

    @classmethod
    def activity(cls):
        activity(cls)

    @classmethod
    def run_with_payload(cls, payload, noclean=False):
        return run(cls, payload, noclean=noclean)

    def process(self, input, **kwargs):
        """ Process a granule locally to produce one or more output granules """
        """
            The Granule class automatically fetches input files and uploads output files, while
            validating both, before and after this process() function. Therefore, the process function
            can retrieve the files from self.input_files[key] where key is the name given to that input
            file (e.g., "hdf-data", "hdf-thumbnail").
            The Granule class takes care of logging, validating, writing out metadata, and reporting on timing
        """
        return {}


if __name__ == "__main__":
    Granule.cli()
