
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

    def __init__(self, filenames, path='', url_paths={}, gid_regex=None, **kwargs):
        """ Initialize a new granule with filenames """
        self.path = path
        self.url_paths = url_paths

        self.local_in = {}
        self.remote_in = {}
        self.local_out = {}
        self.remote_out = {}

        # determine which file is which type of input through use of regular expression
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

        # extract the regex from the first filename
        if gid_regex is not None:
            # get first file passed in
            file0 = filenames[0]
            if isinstance(file0, list):
                file0 = file0[0]
            m = re.match(gid_regex, os.path.basename(file0))
            if m is not None:
                self._gid = ''.join(m.groups())
            else:
                raise ValueError('Unable to determine granule ID from filenames using regex')
        else:
            self._gid = None

        extra = {
            'granuleId': self.gid
        }
        self.logger = logging.LoggerAdapter(logger, extra)

    @property
    def gid(self):
        if self._gid is not None:
            return self._gid
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
                        key = f + '-%s' % i
                        i += 1
                    self.local_in[key] = filename
                else:
                    key = f
                    i = 1
                    while key in self.remote_in:
                        key = f + '-%s' % i
                        i += 1
                    self.remote_in[key] = filename

    def urls(self, filename):
        if len(self.url_paths.keys()) == 0:
            return {'s3': None, 'http': None}
        for pattern in self.url_paths:
            m = re.match(pattern, os.path.basename(filename))
            if m is not None:
                return self.url_paths[pattern]
        self.logger.warning('No URL provided for %s' % filename)
        return {'s3': None, 'http': None}

    def publish(self):
        """ Return URLs for output granule(s), defaults to all public """
        urls = {}
        for gid, gran in self.local_out.items():
            granout = {}
            for key, fname in gran.items():
                url = self.urls(fname)['http']
                if url is not None:
                    granout[key] = os.path.join(self.urls(fname)['http'], os.path.basename(fname))
            urls[gid] = granout
        return urls

    def download_all(self):
        """ Download all files in remote_in """
        return [self.download(key=key) for key in self.remote_in]

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

    def upload(self):
        """ Upload local output files to S3 """
        self.logger.info('uploading output granules')
        for gid, granule in self.local_out.items():
            remote = {}
            for f in granule:
                fname = granule[f]
                if 'hdf' in fname:
                    continue # skip hdf which is already in s3
                urls = self.urls(fname)
                try:
                    if urls['s3'] is not None:
                        extra = {'ACL': 'public-read'} if urls.get('access', 'public') == 'public' else {}
                        uri = s3.upload(fname, urls['s3'], extra=extra)
                        remote[f] = uri
                except Exception as e:
                    self.logger.error("Error uploading file %s: %s" % (os.path.basename(fname), str(e)))
            self.remote_out[gid] = remote
        return [files.values() for files in self.remote_out.values()]

    @classmethod
    def dicttoxml(cls, meta, pretty=False, root='Granule'):
        """ Convert dictionary metadata to XML string """
        # for lists, use the singular version of the parent XML name
        singular_key_func = lambda x: x[:-1]
        # convert to XML
        if root is None:
            xml = dicttoxml(meta, root=False, attr_type=False, item_func=singular_key_func)
        else:
            xml = dicttoxml(meta, custom_root=root, attr_type=False, item_func=singular_key_func)
        # The <Point> XML tag does not follow the same rule as singular
        # of parent since the parent in CMR is <Boundary>. Create metadata
        # with the <Points> parent, and this removes that tag
        xml = xml.replace('<Points>', '').replace('</Points>', '')
        # pretty print
        if pretty:
            dom = parseString(xml)
            xml = dom.toprettyxml()
        return xml

    @classmethod
    def write_metadata(cls, meta, fout, pretty=False):
        """ Write metadata dictionary as XML file """
        xml = cls.dicttoxml(meta, pretty=pretty)
        with open(fout, 'w') as f:
            f.write(xml)

    def clean(self):
        """ Remove input and output files """
        self.logger.info('Cleaning local files')
        for f in self.local_in.values():
            if os.path.exists(f):
                os.remove(f)
        for gran in self.local_out.values():
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
