"""
This testing module relies on some testing data available in s3://cumulus-internal/testing
"""

import os
import uuid
import json
import unittest
from tempfile import mkdtemp
from mock import patch
import cumulus_process.s3 as s3
from cumulus_process import Process

if not os.getenv('LOCALSTACK_HOST'):
    raise Exception('LOCALSTACK_HOST must be set as env variable before running tests')

# mocked function replaced Granule.process
def fake_process(self):
    """ Create local output files as if process did something """
    # produce one fake granu
    Test.create_files(Test.output_files.values())
    for f in Test.output_files:
        self.output.append(Test.output_files[f])
    return self.output


class Test(unittest.TestCase):
    """ Test utiltiies for publishing data on AWS PDS """

    path = mkdtemp() 
    payload = os.path.join(os.path.dirname(__file__), 'payload.json')

    bucket = str(uuid.uuid4()) 
    s3path = 's3://%s/testing/cumulus-py' % bucket
    input_files = [
        os.path.join(s3path, "input-1.txt"),
        os.path.join(s3path, "input-2.txt")
    ]

    output_files = {
        'output-1': os.path.join(path, 'output-1.txt'),
        'output-2': os.path.join(path, 'output-2.txt'),
        'meta': os.path.join(path, 'output-3.meta.xml')
    }

    urls = {
        '.*': {
            's3': s3path,
            'http': 'http://cumulus.com/testing/cumulus-py'
        }
    }

    test_config = {
        'fileStagingDir': '',
        'bucket': bucket 
    }


    @classmethod
    def create_files(cls, filenames):
        """ Create small files for testing """
        fouts = []
        for fname in filenames:
            fout = os.path.join(cls.path, os.path.basename(fname))
            with open(fout, 'w') as f:
                f.write(fname)
            fouts.append(fout)
        return fouts

    @classmethod
    def _setUpClass(cls):
        """ Put some input files up on S3 """
        fouts = cls.create_files(cls.input_files)
        for f in fouts:
            s3.upload(f, cls.s3path)
            os.remove(f)

    def get_test_process(self):
        """ Get Process class for testing """
        with open(self.payload) as f:
            payload = json.loads(f.read())
        return Process(**payload)
        return Process(self.input_files, path=self.path, url_paths=self.urls)

    def test_init(self):
        """ Initialize Granule with JSON payload """
        process = self.get_test_process()
        self.assertTrue(process.input[0], self.input_files[0])
        self.assertTrue(process.input[1], self.input_files[1])

    def test_write_metadata(self):
        """ Write an XML metadata file from a dictionary """
        fout = os.path.join(self.path, 'test_write_metadata.meta.xml')
        Process.write_metadata({'key1': 'val1'}, fout)
        self.assertTrue(os.path.exists(fout))
        os.remove(fout)

    def test_config_input_keys(self):
        """ Test getting input_keys from config """
        with open(self.payload) as f:
            payload = json.loads(f.read())
            process = Process(**payload)
            assert process.input_keys['from_config']

    def test_invalid_input_keys(self):
        """ Test getting invalid input_keys from config """
        with open(self.payload) as f:
            payload = json.loads(f.read())
            payload['config']['input_keys'] = 'not a dict'
            with self.assertRaises(Exception):
                Process(**payload)

    def test_missing_input_keys(self):
        """ Test use default_keys if no input_keys in payload """
        with open(self.payload) as f:
            payload = json.loads(f.read())
            del payload['config']['input_keys']
            process = Process(**payload)
            assert process.has_default_keys

    @patch.object(Process, 'process', fake_process)
    def test_upload(self):
        """ Upload output files """
        process = self.get_test_process()
        process.process()
        process.clean_all()

    @patch.object(Process, 'process', fake_process)
    def test_run(self):
        """ Make complete run """
        output = Process.run(self.input_files, path=mkdtemp(),
                             config=self.test_config, noclean=True)
        # check for local output files
        for f in self.output_files.values():
            self.assertTrue(os.path.exists(f))
            self.assertTrue(f in output)

    def _check_and_remove_remote_out(self, uris):
        """ Check for existence of remote files, then remove them """
        for uri in uris:
            self.assertTrue(s3.exists(uri))
            s3.delete(uri)
            self.assertFalse(s3.exists(uri))
