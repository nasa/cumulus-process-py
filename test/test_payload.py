import os
import json
import unittest
import cumulus.s3 as s3
from cumulus.payload import Payload
from nose.tools import raises


class TestPayload(unittest.TestCase):
    """ Test utiltiies for publishing data on AWS PDS """

    s3path = 's3://cumulus-internal/testing/cumulus-py'
    testdir = os.path.dirname(__file__)
    payload = os.path.join(testdir, 'payload.json')

    def get_payload(self):
        """ Get payload object """
        return Payload(self.payload)

    def test_parse_payload_json(self):
        """ Parse JSON payload """
        with open(self.payload, 'r') as f:
            payload = json.loads(f.read())
        pl = Payload(payload)
        param = pl.process_parameters()
        self.assertTrue('gid' in param)
        self.assertEqual(len(param['filenames']), 2)

    def test_parse_payload_string(self):
        """ Parse JSON string payload """
        with open(self.payload, 'r') as f:
            payload = f.read()
        pl = Payload(payload)
        param = pl.process_parameters()
        self.assertTrue('gid' in param)
        self.assertEqual(len(param['filenames']), 2)

    def test_parse_payload_file(self):
        """ Parse test payload file """
        pl = Payload(self.payload)
        param = pl.process_parameters()
        self.assertTrue('gid' in param)
        self.assertEqual(len(param['filenames']), 2)

    def test_parse_payload_from_s3(self):
        """ Parse test payload from S3 file """
        uri = s3.upload(self.payload, self.s3path)
        pl = Payload(uri)
        param = pl.process_parameters()
        self.assertTrue('gid' in param)
        self.assertEqual(len(param['filenames']), 2)

    @raises(ValueError)
    def test_parse_invalid_payload(self):
        """ Parse invalid payload """
        Payload('nonsensestring')
