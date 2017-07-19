"""
This testing module relies on some testing data available in s3://cumulus-internal/testing
"""

import os
import unittest
from mock import patch
import cumulus.s3 as s3
from cumulus.granule import Granule
from cumulus.aws import run


# mocked function replaced Granule.process
def fake_process(self):
    """ Create local output files as if process did something """
    # produce one fake granu
    TestAWS.create_files(TestAWS.output_files.values())
    local_out = {}
    for f in TestAWS.output_files:
        local_out[f] = TestAWS.output_files[f]
    self.local_out.append(local_out)


class TestAWS(unittest.TestCase):
    """ Test utiltiies for publishing data on AWS PDS """

    s3path = 's3://cumulus-internal/testing/cumulus-py'
    path = os.path.dirname(__file__)
    payload = os.path.join(path, 'payload.json')

    input_files = [
        os.path.join(s3path, "input-1.txt"),
        os.path.join(s3path, "input-2.txt")
    ]

    output_files = {
        'out1': os.path.join(path, 'output-1.txt'),
        'out2': os.path.join(path, 'output-2.txt'),
        'meta': os.path.join(path, 'output-3.meta.xml')
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
        fouts = cls.create_files(cls.input_files)
        for f in fouts:
            s3.upload(f, cls.s3path)
            os.remove(f)

    @classmethod
    def tearDownClass(cls):
        for f in cls.input_files:
            s3.delete(f)

    @patch.object(Granule, 'process', fake_process)
    def test_run(self):
        """ Make complete run with payload """
        payload = run(Granule, self.payload, path=self.path, s3path=self.s3path)
        outputs = payload['payload']['output']
        uris = [uri for c in outputs for g in outputs[c]['granules'] for uri in g.values()]
        self.check_and_remove_remote_out(uris)

    def check_and_remove_remote_out(self, uris):
        """ Check for existence of remote files, then remove them """
        for uri in uris:
            self.assertTrue(s3.exists(uri))
            s3.delete(uri)
            self.assertFalse(s3.exists(uri))
