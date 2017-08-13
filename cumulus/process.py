
import os
import re
import subprocess
import logging
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
import cumulus.s3 as s3
from cumulus.loggers import getLogger
from cumulus.cli import cli
from cumulus.aws import run, activity

logger = getLogger(__name__)


class Process(object):
    """ Class representing a data granule on S3 and processing that granule """

    # internally used keys
    inputs = {
        'input-1': r'^.*-1.txt$',
        'input-2': r'^.*-2.txt$'
    }

    autocheck = True

    def __init__(self, filenames, path='', url_paths={}, **kwargs):
        """ Initialize a new granule with filenames """
        self.path = path
        self.url_paths = url_paths

        self.local_in = {}
        self.local_out = []
        self.remote_out = []
        # determine which file is which type of input through use of regular expression
        self.remote_in = {}

        for el in filenames:
            if isinstance(el, list):
                for f in el:
                    self.add_input_file(f)
            else:
                self.add_input_file(el)

        # let child data granules determine if it's not enough
        if self.autocheck:
            totalfiles = len(self.remote_in) + len(self.local_in)
            if (len(self.inputs) != totalfiles):
                raise IOError('Files do not make up complete granule or extra files provided')

        extra = {
            'granuleId': self.gid
        }
        self.logger = logging.LoggerAdapter(logger, extra)

    @property
    def gid(self):
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
                if os.path.exists(filename):
                    # add as new unused key
                    key = f
                    i = 1
                    while key in self.local_in:
                        key = key + '-%s' % i
                        i += 1
                    self.local_in[key] = filename
                else:
                    key = f
                    i = 1
                    while key in self.remote_in:
                        key = key + '-%s' % i
                        i += 1
                    self.remote_in[key] = filename

    def urls(self, filename):
        if len(self.url_paths.keys()) == 0:
            return {'s3': None, 'http': None}
        for pattern in self.url_paths:
            m = re.match(pattern, os.path.basename(filename))
            if m is not None:
                return self.url_paths[pattern]

    def publish(self):
        """ Return URLs for output granule(s), defaults to all public """
        urls = []
        for gran in self.local_out:
            granout = {}
            for key, fname in gran.items():
                # get url
                url = self.urls(fname)['http']
                if url is not None:
                    granout[key] = os.path.join(self.urls(fname)['http'], os.path.basename(fname))
            urls.append(granout)
        return urls

    def download(self, key=None):
        """ Download input file from S3 """
        keys = self.inputs.keys() if key is None else [key]
        downloaded = []
        for key in keys:
            if key not in self.local_in:
                uri = self.remote_in[key]
                self.logger.info('downloading input file %s' % uri)
                fname = s3.download(uri, path=self.path)
                self.local_in[key] = fname
            else:
                fname = self.local_in[key]
            downloaded.append(str(fname))
        return downloaded

    def s3path(self, key):
        """ Get bucket for this key """
        vis = self.visibility.get(key, 'public')
        s3path = self.s3paths.get(vis, None)
        if s3path is None and '' in self.s3paths:
            s3path = self.s3paths['']
        return s3path

    def upload(self):
        """ Upload local output files to S3 """
        self.logger.info('uploading output granules')
        for granule in self.local_out:
            remote = {}
            for f in granule:
                fname = granule[f]
                s3url = self.urls(fname)['s3']
                try:
                    if s3url is not None:
                        uri = s3.upload(fname, s3url)
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
            import traceback
            self.logger.error({'message': 'Run error with granule: %s' % str(e),
                              'error': traceback.format_exc()})
            raise e

    def run_command(self, cmd):
        """ Run cmd as a system command """
        try:
            self.logger.debug(cmd)
            out = subprocess.check_output(cmd.split(' '), stderr=subprocess.STDOUT)
            self.logger.debug(out)
            return out
        except Exception as e:
            self.logger.debug(str(e))
            raise RuntimeError('Error running %s' % cmd)

    @classmethod
    def add_parser_args(cls, parser):
        """ Add class specific arguments to the parser """
        return parser

    @classmethod
    def cli(cls):
        cli(cls)

    @classmethod
    def activity(cls, arn=os.getenv('ACTIVITY_ARN')):
        activity(cls, arn=arn)

    @classmethod
    def run_with_payload(cls, payload, **kwargs):
        return run(cls, payload, **kwargs)

    def process(self, **kwargs):
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
    Process.cli()
