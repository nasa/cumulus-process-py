"""
This testing module relies on some testing data available in s3://cumulus-internal/testing
"""

import os
import uuid
import json
import unittest
from shutil import rmtree
from tempfile import mkdtemp
from example.main import Modis 
import cumulus_process.s3 as s3
from cumulus_process import Process, helpers

if not os.getenv('LOCALSTACK_HOST'):
    raise Exception('LOCALSTACK_HOST must be set as env variable before running tests')

class TestExample(unittest.TestCase):
    """Test the example implementation of the Process class"""

    bucket = str(uuid.uuid4()) 
    s3path = 's3://%s/testing/cumulus-py' % bucket
    path = mkdtemp()
    payload = os.path.join(os.path.dirname(__file__), 'payload.json')

    input_files = [
        os.path.join(s3path, "MOD09GQ.A2016358.h13v04.006.2016360104606.hdf"),
        os.path.join(s3path, "MOD09GQ.A2016358.h13v04.006.2016360104606.hdf.met"),
        os.path.join(s3path, "BROWSE.MOD09GQ.A2016358.h13v04.006.2016360104606.hdf")
    ]

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
    def setUpClass(cls):
        """ Put some input files up on S3 """
        # create the bucket first
        cls.s3 = s3.get_client()
        cls.s3.create_bucket(Bucket=cls.bucket)

        fouts = cls.create_files(cls.input_files)
        for f in fouts:
            s3.upload(f, os.path.join(cls.s3path, os.path.basename(f)))
        
    @classmethod
    def tearDownClass(cls):
        # delete the bucket
        uris = s3.list_objects('s3://%s' % cls.bucket)
        [s3.delete(uri) for uri in uris]
        cls.s3.delete_bucket(Bucket=cls.bucket)

        # delete temp folder
        rmtree(cls.path)

    def test_example(self):
        """ Make complete run with payload """
        with open(self.payload, 'rb') as data:
            input_payload = json.loads(data.read())
            input_payload['input'] = self.input_files
            input_payload['config']['bucket'] = self.bucket
            payload = Modis.run(input_payload['input'], path=self.path, config=input_payload['config'], noclean=True)
            # assumes first granule is input, all others output
            self.assertEqual(len(payload), 4)
            self.assertEqual(os.path.basename(payload[3]), 'new_file.jpg')
            self.check_and_remove_remote_out(payload)

    def check_and_remove_remote_out(self, uris):
        """ Check for existence of remote files, then remove them """
        for uri in uris:
            self.assertTrue(s3.exists(uri))
            s3.delete(uri)
            self.assertFalse(s3.exists(uri))
