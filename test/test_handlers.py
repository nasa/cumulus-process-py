"""
This testing module relies on some testing data available in s3://cumulus-internal/testing
"""

import os
import uuid
import json
import unittest
from mock import patch
import cumulus_process.s3 as s3
from cumulus_process import Process


# mocked function replaced Process.process
def fake_process(self):
    """ Create local output files as if process did something """
    # produce one fake granu
    TestAWS.create_files(TestAWS.output_files.values())
    local_out = {}
    for f in TestAWS.output_files:
        local_out[f] = TestAWS.output_files[f]
    self.output = local_out.values();
    return self.upload_output_files()


class TestAWS(unittest.TestCase):
    """ Test utiltiies for publishing data on AWS PDS """

    bucket = str(uuid.uuid4()) 
    s3path = 's3://%s/testing/cumulus-py' % bucket
    path = os.path.dirname(__file__)
    payload = os.path.join(path, 'payload.json')

    input_files = [
        os.path.join(s3path, "input-1.txt"),
        os.path.join(s3path, "input-2.txt")
    ]

    output_files = {
        'output-1': os.path.join(path, 'output-1.txt'),
        'output-2': os.path.join(path, 'output-2.txt'),
        'meta': os.path.join(path, 'output-3.cmr.xml')
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
    def setUpClass(cls):
        """ Put some input files up on S3 """
        # create the bucket first
        cls.s3 = s3.get_client()
        cls.s3.create_bucket(Bucket=cls.bucket)

        fouts = cls.create_files(cls.input_files)
        for f in fouts:
            s3.upload(f, cls.s3path)
            os.remove(f)

    @classmethod
    def tearDownClass(cls):
        files = s3.list_objects('s3://%s' % cls.bucket)
        for f in files:
            s3.delete(f)

        # delete the bucket
        cls.s3.delete_bucket(Bucket=cls.bucket)


    @patch.object(Process, 'process', fake_process)
    def _test_run(self):
        """ Make complete run with payload """
        with open(self.payload, 'rb') as data:
            payload = Process.handler(json.loads(data.read()), path=self.path)
            # assumes first granule is input, all others output
            print(payload)
            self.assertEqual(len(payload), 3)
            self.check_and_remove_remote_out(uris)

    def check_and_remove_remote_out(self, uris):
        """ Check for existence of remote files, then remove them """
        for uri in uris:
            self.assertTrue(s3.exists(uri))
            s3.delete(uri)
            self.assertFalse(s3.exists(uri))
