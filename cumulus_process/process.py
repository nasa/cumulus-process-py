
import os
import re
import gzip
import subprocess
import logging
import warnings
from shutil import rmtree
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
        keys = self.config.get('input_keys')
        return self.default_keys if keys == None else keys

    @property
    def default_keys(self):
        """ Keys used to reference files internally """
        self.has_default_keys = True
        return {
            'input-1': r'^.*-1.txt$',
            'input-2': r'^.*-2.txt$'
        }

    def process(self):
        """ Process data to produce one or more output granules """
        NotImplementedError(
            'This method is not implemented in the base process ' +
            'class and MUST be implemented in subclasses of process'
        )

    @property
    def gid(self):
        """ Get GID based on regex if provided """
        warnings.warn(
            'gid property is deprecated and will be removed in the next release',
            DeprecationWarning
        )
        gid = None

        if not isinstance(self.input, list):
            return gid

        if self.regex is not None:
            # get first file passed in
            file0 = self.input[0]
            m = re.match(self.regex, os.path.basename(file0))
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
        self.input = input
        self.regex = None

        # check valid input keys
        if not isinstance(self.input_keys, dict):
            raise Exception('Input keys must be a dictionary')

        # save downloaded files so we can clean up later
        self.downloads = []

        # output granules
        self.output = []

        # set up logger
        self.logger = logging.LoggerAdapter(logger, {})

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
        warnings.warn(
            'fetch_all method is deprecated and will be removed in the next release',
            DeprecationWarning
        )
        return {key: self.fetch(key=key, remote=remote) for key in self.input_keys}

    def upload_file(self, filename):
        """ Upload a local file to s3 if collection payload provided """
        warnings.warn(
            'upload_file method is deprecated and will be removed in the next release. ' +
            'use upload functions in s3 module instead',
            DeprecationWarning
        )
        info = self.get_publish_info(filename)
        if info is None:
            return filename
        try:
            return upload(filename, info['s3'], extra={}) if info.get('s3', False) else None
        except Exception as e:
            self.logger.error("Error uploading file %s: %s" % (os.path.basename(os.path.basename(filename)), str(e)))

    def upload_output_files(self):
        """ Uploads all self.outputs """
        warnings.warn(
            'upload_output_files method is deprecated and will be removed in the next release. ' +
            'use helper functions from the helper module instead',
            DeprecationWarning
        )
        return [self.upload_file(f) for f in self.output]

    def clean_downloads(self):
        """ Remove input files """
        warnings.warn(
            'clean_downloads method is deprecated and will be removed in the next release',
            DeprecationWarning
        )
        self.logger.info('Cleaning downloaded files')
        for f in self.downloads:
            if os.path.exists(f) and f not in self.output:
                os.remove(f)

    def clean_output(self):
        """ Remove local output files """
        warnings.warn(
            'clean_output method is deprecated and will be removed in the next release',
            DeprecationWarning
        )
        for f in self.output:
            if os.path.exists(f):
                os.remove(f)

    def clean_all(self):
        """ Removes anything saved to self.path """
        rmtree(self.path)

    # ## Publishing functions
    # properties to access payload parameters for publishing
    @property
    def buckets(self):
        warnings.warn(
            'buckets property is deprecated and will be removed in the next release',
            DeprecationWarning
        )
        return self.config.get('buckets', {})

    @property
    def collection(self):
        warnings.warn(
            'collection property is deprecated and will be removed in the next release',
            DeprecationWarning
        )
        return self.config.get('collection', {})

    @property
    def default_url(self):
        """ Get default endpoint """
        warnings.warn(
            'default_url property is deprecated and will be removed in the next release',
            DeprecationWarning
        )
        return self.config.get('distribution_endpoint', 'https://cumulus.com')

    def get_publish_info(self, filename):
        """ Get publishing info for this file from the collection metadata """
        warnings.warn(
            'get_publish_info method is deprecated and will be removed in the next release',
            DeprecationWarning
        )
        files = self.config.get('files_config', [])
        info = None
        count = 0
        for f in files:
            m = re.match(f['regex'], os.path.basename(filename))
            if m is not None:
                count += 1
                info = f
                file_bucket = f.get('bucket', 'public')
                bucket = self.buckets.get(file_bucket, None)
                if bucket is not None:
                    prefix = f.get('fileStagingDir', self.config.get('fileStagingDir', ''))
                    if prefix is None:
                        prefix = f.get('url_path', self.config.get('url_path', ''))
                    s3_url = os.path.join('s3://', bucket['name'], prefix, os.path.basename(filename))
                    http_url = 'http://%s.s3.amazonaws.com' % bucket['name'] if bucket['type'] == 'public' else self.default_url
                    http_url = os.path.join(http_url, prefix, os.path.basename(filename))
                    info.update({'s3': s3_url, 'http': http_url})
        if (count) > 1:
            raise Exception('More than one regex matches %s' % filename)
        return info

    # ## Utility functions

    @classmethod
    def dicttoxml(cls, meta, pretty=False, root='Granule'):
        """ Convert dictionary metadata to XML string """
        warnings.warn(
            'dicttoxml method is deprecated and will be removed in the next release. ' +
            'use helper functions from the helper module instead',
            DeprecationWarning
        )
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
        warnings.warn(
            'write_metadata method is deprecated and will be removed in the next release. ' +
            'use helper functions from the helper module instead',
            DeprecationWarning
        )
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
        warnings.warn(
            'gunzip method is deprecated and will be removed in the next release. ' +
            'use helper functions from the helper module instead',
            DeprecationWarning
        )
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
        warnings.warn(
            'basename method is deprecated and will be removed in the next release. ' +
            'use helper functions from the helper module instead',
            DeprecationWarning
        )
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
        try:
            output = process.process()
        finally:
            if not noclean:
                process.clean_all()
        return output


if __name__ == "__main__":
    Process.cli()
