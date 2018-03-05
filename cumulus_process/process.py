
import os
import re
import gzip
import subprocess
import logging
from tempfile import mkdtemp
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
from cumulus_process.s3 import download, upload
from cumulus_process.loggers import getLogger
from cumulus_process.cli import cli
from cumulus_process.handlers import activity
from run_cumulus_task import run_cumulus_task

logger = getLogger(__name__)


class Process(object):
    """ Class representing a data granule on S3 and processing that granule """

    @property
    def input_keys(self):
        """ Keys used to reference files internally """
        return {
            'input-1': r'^.*-1.txt$',
            'input-2': r'^.*-2.txt$'
        }

    def process(self):
        """ Process data to produce one or more output granules """
        return {}

    @property
    def gid(self):
        """ Get GID based on regex if provided """
        gid = None
        regex = self.config.get('granuleIdExtraction', None)
        if regex is not None:
            # get first file passed in
            file0 = self.input[0]
            m = re.match(regex, os.path.basename(file0))
            if m is not None:
                gid = ''.join(m.groups())
        if gid is None:
            # try and determine an GID from a commonprefix
            gid = os.path.commonprefix([self.basename(f) for f in self.input])
        if gid == '':
            # make gid the basename within extension of first file
            gid = self.basename(self.input[0])
        return gid

    @classmethod
    def add_parser_args(cls, parser):
        """ Add class specific arguments to the parser """
        return parser

    def __init__(self, input, path=None, config={}, **kwargs):
        """ Initialize a Process with input filenames and optional kwargs """
        # local work directory files will be stored
        if path is None:
            path = mkdtemp()
        self.path = path
        self.config = config
        self.kwargs = kwargs

        # check for required configs
        required = ['granuleIdExtraction', 'files_config', 'buckets']

        for requirement in required:
            if requirement not in self.config.keys():
                raise Exception('%s config key is missing' % requirement)

        # list of input filenames
        if not isinstance(input, list):
            raise Exception('cumulus-process-py expects to receive input as a list')
        self.input = input

        # save downloaded files so we can clean up later
        self.downloads = []

        # output granules
        self.output = []

        # set up logger
        extra = {'granuleId': self.gid}
        self.logger = logging.LoggerAdapter(logger, extra)

    def fetch(self, key, remote=False):
        """ Get local (default) or remote input filename """
        regex = self.input_keys.get(key, None)
        if regex is None:
            raise Exception('No files matching %s' % regex)
        outfiles = []
        for f in self.input:
            m = re.match(regex, os.path.basename(f))
            if m is not None:
                # if remote desired, or input is already local
                if remote or os.path.exists(f):
                    outfiles.append(f)
                else:
                    fname = download(f, path=self.path)
                    outfiles.append(fname)
                    self.downloads.append(fname)
        return outfiles

    def fetch_all(self, remote=False):
        """ Download all files in remote_in """
        return {key: self.fetch(key=key, remote=remote) for key in self.input_keys}

    def upload_file(self, filename):
        """ Upload a local file to s3 if collection payload provided """
        info = self.get_publish_info(filename)
        if info is None:
            return filename
        try:
            uri = None
            if info.get('s3', None) is not None:
                extra = {'ACL': 'public-read'} if info.get('bucket', 'public') == 'public' else {}
                uri = upload(filename, info['s3'], extra=extra)
            return uri
        except Exception as e:
            self.logger.error("Error uploading file %s: %s" % (os.path.basename(os.path.basename(filename)), str(e)))

    def upload_output_files(self):
        """ Uploads all self.outputs """
        return [self.upload_file(f) for f in self.output]

    def clean_downloads(self):
        """ Remove input files """
        self.logger.info('Cleaning downloaded files')
        for f in self.downloads:
            if os.path.exists(f) and f not in self.output:
                os.remove(f)

    def clean_output(self):
        """ Remove local output files """
        for f in self.output:
            if os.path.exists(f):
                os.remove(f)

    def clean_all(self):
        """ Remove all local files """
        self.clean_downloads()
        self.clean_output()

    # ## Publishing functions
    # properties to access payload parameters for publishing
    @property
    def buckets(self):
        return self.config.get('buckets', {})

    @property
    def collection(self):
        return self.config.get('collection', {})

    @property
    def default_url(self):
        """ Get default endpoint """
        return self.config.get('distribution_endpoint', 'https://cumulus.com')

    def get_publish_info(self, filename):
        """ Get publishing info for this file from the collection metadata """
        files = self.config.get('files_config', [])
        info = None
        count = 0
        for f in files:
            m = re.match(f['regex'], os.path.basename(filename))
            if m is not None:
                count += 1
                info = f
                access = f.get('bucket', 'public')
                bucket = self.buckets.get(access, None)
                if bucket is not None:
                    prefix = f.get('url_path', self.config.get('url_path', ''))
                    if prefix is None:
                        prefix = ''
                    s3_url = os.path.join('s3://', bucket, prefix, os.path.basename(filename))
                    http_url = 'http://%s.s3.amazonaws.com' % bucket if access == 'public' else self.default_url
                    http_url = os.path.join(http_url, prefix, os.path.basename(filename))
                    info.update({'s3': s3_url, 'http': http_url})
        if (count) > 1:
            raise Exception('More than one regex matches %s' % filename)
        return info

    # ## Utility functions

    @classmethod
    def dicttoxml(cls, meta, pretty=False, root='Granule'):
        """ Convert dictionary metadata to XML string """
        # for lists, use the singular version of the parent XML name
        singular_key_func = lambda x: x[:-1]
        # convert to XML
        if root is None:
            xml = str(dicttoxml(meta, root=False, attr_type=False, item_func=singular_key_func))
        else:
            xml = str(dicttoxml(meta, custom_root=root, attr_type=False, item_func=singular_key_func))
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
    def gunzip(cls, fname, remove=False):
        """ Unzip a file, creating new file """
        f = os.path.splitext(fname)[0]
        with gzip.open(fname, 'rb') as fin:
            with open(f, 'wb') as fout:
                fout.write(fin.read())
        if remove:
            os.remove(fname)
        return f

    @classmethod
    def basename(cls, filename):
        """ Strip path and extension """
        return os.path.splitext(os.path.basename(filename))[0]

    # ## Handlers
    @classmethod
    def handler(cls, event, context=None, path=None, noclean=False):
        """ General event handler """
        return cls.run(path=path, noclean=noclean, **event)

    @classmethod
    def cumulus_handler(cls, event, context=None):
        """ General event handler using Cumulus messaging (cumulus-message-adapter) """
        return run_cumulus_task(cls.handler, event, context)

    @classmethod
    def cli(cls):
        cli(cls)

    @classmethod
    def activity(cls, arn=os.getenv('ACTIVITY_ARN')):
        """ Run an AWS activity for a step function """
        activity(cls.handler, arn)

    @classmethod
    def cumulus_activity(cls, arn=os.getenv('ACTIVITY_ARN')):
        """ Run an activity using Cumulus messaging (cumulus-message-adapter) """
        activity(cls.cumulus_handler, arn)

    @classmethod
    def run(cls, *args, **kwargs):
        """ Run this payload with the given Process class """
        noclean = kwargs.pop('noclean', False)
        process = cls(*args, **kwargs)
        output = process.process()
        if not noclean:
            process.clean_all()
        return output


if __name__ == "__main__":
    Process.cli()
