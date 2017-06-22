import os
import json
import unittest
import cumulus.s3 as s3
from cumulus.payload import parse_payload
from nose.tools import raises


class TestPayload(unittest.TestCase):
    """ Test utiltiies for publishing data on AWS PDS """

    s3path = 's3://cumulus-internal/testing/cumulus-py'
    testdir = os.path.dirname(__file__)
    payload = os.path.join(testdir, 'payload.json')

    def test_parse_payload_json(self):
        """ Parse JSON payload """
        with open(self.payload, 'r') as f:
            payload = json.loads(f.read())
        payload = parse_payload(payload)
        self.assertTrue('gid' in payload)
        self.assertEqual(len(payload['filenames']), 2)

    def test_parse_payload_string(self):
        """ Parse JSON string payload """
        with open(self.payload, 'r') as f:
            payload = f.read()
        payload = parse_payload(payload)
        self.assertTrue('gid' in payload)
        self.assertEqual(len(payload['filenames']), 2)

    def test_parse_payload_file(self):
        """ Parse test payload file """
        payload = parse_payload(self.payload)
        self.assertTrue('gid' in payload)
        self.assertEqual(len(payload['filenames']), 2)

    def test_parse_payload_from_s3(self):
        """ Parse test payload from S3 file """
        uri = s3.upload(self.payload, self.s3path)
        payload = parse_payload(uri)
        self.assertTrue('gid' in payload)
        self.assertEqual(len(payload['filenames']), 2)

    @raises(ValueError)
    def test_parse_invalid_payload(self):
        """ Parse invalid payload """
        parse_payload('nonsensestring')
