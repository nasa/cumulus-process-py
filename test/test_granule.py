"""
This testing module relies on some testing data available in s3://cumulus-internal/testing
"""

import os
import unittest
import logging
import json
import cumulus.s3 as s3
from cumulus.granule import Granule

# quiet these loggers
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)


class TestGranule(unittest.TestCase):
    """ Test utiltiies for publishing data on AWS PDS """

    bucket = 'cumulus-internal'
    testdir = os.path.dirname(__file__)
    payload = os.path.join(testdir, 'payload.json')

    def uri(self, key):
        return 's3://%s' % os.path.join(self.bucket, key)

    def test_init(self):
        """ Initialize Granule with JSON payload """
        with open(self.payload, 'r') as f:
            payload = json.loads(f.read())
        self.assertTrue('granuleRecord' in payload.keys())
        granule = Granule(payload)
        self.assertTrue('granuleRecord' in granule.payload.keys())

    def test_init_s3(self):
        """ Initialize granule with payload retrieved from s3 """
        uri = s3.upload(self.payload, self.uri('testing'))
        granule = Granule(uri)
        self.assertTrue('granuleRecord' in granule.payload.keys())
        s3.delete(uri)
        self.assertFalse(s3.exists(uri))

    def test_init_file(self):
        """ initialize Ganule with payload JSON file """
        granule = Granule(self.payload)
        self.assertTrue('granuleRecord' in granule.payload.keys())

    def test_recipe(self):
        """ Get recipe from payload """
        granule = Granule(self.payload)
        self.assertTrue('archive' in granule.recipe)
        self.assertTrue('order' in granule.recipe)
        self.assertTrue('processStep' in granule.recipe)

    def test_metadata(self):
        """ Get metadata for granule """
        granule = Granule(self.payload)
        md = granule.metadata()
        self.assertTrue('<Granule>' in md)
        self.assertTrue('<GranuleUR>%s</GranuleUR>' % granule.id in md)

    def test_metadata_file(self):
        """ Save metadata as file """
        granule = Granule(self.payload, path=self.testdir)
        fout = granule.metadata(save=True)
        self.assertTrue(os.path.exists(fout))
        os.remove(fout)

    def test_input_files(self):
        """ Get input files parsed from payload """
        granule = Granule(self.payload)
        files = granule.input_files
        self.assertEqual(len(files), 2)
        for i in ['input-1', 'input-2']:
            self.assertTrue(i in files)

    def test_output_files(self):
        """ Get output files parsed from payload """
        granule = Granule(self.payload)
        files = granule.output_files
        self.assertEqual(len(files), 2)
        for o in ['output-1', 'output-2', 'meta-xml']:
            self.assertTrue(o in files)

    def test_download(self):
        """ Download input files given in payload """
        granule = Granule(self.payload, path=self.testdir)
        fnames = granule.download()
        self.assertEqual(len(fnames), 2)
        for f in fnames:
            self.assertTrue(os.path.exists(fnames[f]))
            os.remove(fnames[f])

    def test_upload(self):
        """ Upload output files given in payload """
        granule = Granule(self.payload, path=self.testdir)
        uris = granule.upload(self.uri('testing/cumulus-py'))
        for uri in uris:
            self.assertTrue(s3.exists(uri))
            s3.delete(uri)
            self.assertFalse(s3.exists(uri))

    def test_run(self):
        """ Make complete run with the run function """
        granule = Granule(self.payload, path=self.testdir)
        granule.run()
        # check for metadata
        # get log output to check for all success messages
