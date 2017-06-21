
import os
import re
import logging
import json
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
import cumulus.s3 as s3
from cumulus.loggers import getLogger

logger = getLogger(__name__)


class Granule(object):
    """ Class representing a data granule on S3 and processing that granule """

    # internally used keys
    inputs = {
        'hdf': '*.hdf$',
        'meta': '*.met'
    }
    outputs = {
        'hdf': '*_out.hdf',
        'meta-xml': '*.xml'
    }

    def __init__(self, gid, filenames, collection='granule', path='', s3path='', **kwargs):
        """ Initialize a new granule with filenames """
        self.gid = gid
        self.collection = collection

        # determine which file is which type of input through use of regular expression
        self.remote_in = {}
        for f in filenames:
            for i in self.inputs:
                m = re.match(self.inputs[i], f)
                if m is not None:
                    if i not in self.remote_in:
                        self.remote_in[i] = f
                    else:
                        raise IOError('Multiple input files for %s given' % i)
        if len(self.inputs) != len(self.remote_in):
            raise IOError('Files do not make up complete granule')

        extra = {
            'collectionName': self.collection,
            'granuleId': self.gid
        }
        self.logger = logging.LoggerAdapter(logger, extra)

        self.local_in = {}
        self.local_out = []
        self.remote_out = []

    def publish(self, visibility={}, protected_url='http://cumulus.com'):
        """ Return URLs for output granule(s), defaults to all public """
        s3obj = self.s3path.split('/')
        public = 'http://%s.s3.amazonaws.com' % s3obj[0]
        if len(s3obj) > 1:
            for d in s3obj[1:]:
                public = os.path.join(public, d)

        urls = {}
        for gran in self.remote_out:
            granout = {}
            for key in gran:
                vis = visibility.get(key, 'public')
                if vis == 'public':
                    granout[key] = os.path.join(public, gran[key])
                elif vis == 'protected':
                    granout[key] = os.path.join(protected_url, gran[key])
            urls.append(granout)
        return urls

    def download(self, key):
        """ Download input file from S3 """
        uri = self.remote_in[key]
        self.logger.info('downloading input file %s' % uri)
        fname = s3.download(uri, path=self.path)
        self.local_in[key] = fname

    def upload(self):
        """ Upload local output files to S3 """
        self.logger.info('uploading output granules to %s' % self.s3path)
        for granule in self.local_out:
            if len(granule) < len(self.outputs):
                self.logger.warning("Not all output files were available for upload")
            for f in granule:
                fname = granule[f]
                try:
                    uri = s3.upload(fname, self.s3path)
                    self.remote_out[f] = uri
                except Exception as e:
                    self.logger.error("Error uploading file %s: %s" % (os.path.basename(fname), str(e)))

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
        """ Run all steps and log: download, process, upload """
        try:
            self.logger.info('begin processing')
            self.logger.info('download input files')
            for f in self.filenames:
                self.download(f)
            self.logger.info('processing')
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
