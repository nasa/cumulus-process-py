import os
import json
import unittest
import cumulus.s3 as s3
from cumulus.payload import Payload
from nose.tools import raises


testpath = os.path.dirname(__file__)


class TestPayload(unittest.TestCase):
    """ Test utiltiies for publishing data on AWS PDS """

    s3path = 's3://cumulus-internal/testing/cumulus-py'
    payload = os.path.join(testpath, 'payload.json')

    def get_payload(self):
        """ Get local payload object """
        return Payload(self.payload)

    def test_parse_payload_json(self):
        """ Parse JSON payload """
        with open(self.payload, 'r') as f:
            payload = json.loads(f.read())
        pl = Payload(payload)
        filenames = pl.input_filenames()
        self.assertEqual(len(filenames), 2)

    def test_parse_payload_string(self):
        """ Parse JSON string payload """
        with open(self.payload, 'r') as f:
            payload = f.read()
        pl = Payload(payload)
        filenames = pl.input_filenames()
        self.assertEqual(len(filenames), 2)

    def test_parse_payload_file(self):
        """ Parse test payload file """
        pl = Payload(self.payload)
        filenames = pl.input_filenames()
        self.assertEqual(len(filenames), 2)

    def test_parse_payload_from_s3(self):
        """ Parse test payload from S3 file """
        uri = s3.upload(self.payload, self.s3path)
        pl = Payload(uri)
        filenames = pl.input_filenames()
        self.assertEqual(len(filenames), 2)

    @raises(ValueError)
    def test_parse_invalid_payload(self):
        """ Parse invalid payload """
        Payload('nonsensestring')
