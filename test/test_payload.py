import os
import sys
import json
import unittest
import logging
import cumulus.s3 as s3
from cumulus.payload import Payload
from nose.tools import raises

logging.basicConfig(stream=sys.stdout)

testpath = os.path.dirname(__file__)


class TestPayload(unittest.TestCase):
    """ Test utiltiies for publishing data on AWS PDS """

    s3path = 's3://cumulus-internal/testing/cumulus-py'
    payload = os.path.join(testpath, 'payload.json')

    def get_payload(self):
        """ Get local payload object """
        return Payload(self.payload)

    def get_payload_json(self):
        """ Get payload as JSON """
        with open(self.payload, 'r') as f:
            payload = json.loads(f.read())
        return payload

    def test_parse_payload_json(self):
        """ Parse JSON payload """
        with open(self.payload, 'r') as f:
            payload = json.loads(f.read())
        pl = Payload(payload)
        filenames = pl.filenames()
        self.assertEqual(len(filenames), 1)
        self.assertEqual(len(filenames[0]), 2)

    def test_parse_payload_string(self):
        """ Parse JSON string payload """
        with open(self.payload, 'r') as f:
            payload = f.read()
        pl = Payload(payload)
        filenames = pl.filenames()
        self.assertEqual(len(filenames), 1)
        self.assertEqual(len(filenames[0]), 2)

    def test_parse_payload_file(self):
        """ Parse test payload file """
        pl = Payload(self.payload)
        filenames = pl.filenames()
        self.assertEqual(len(filenames), 1)
        self.assertEqual(len(filenames[0]), 2)

    def test_parse_payload_from_s3(self):
        """ Parse test payload from S3 file """
        uri = s3.upload(self.payload, self.s3path)
        pl = Payload(uri)
        filenames = pl.filenames()
        self.assertEqual(len(filenames), 1)
        self.assertEqual(len(filenames[0]), 2)

    @raises(ValueError)
    def test_parse_invalid_payload(self):
        """ Parse invalid payload """
        Payload('nonsensestring')

    @raises(ValueError)
    def test_parse_invalid_payload2(self):
        """ Parse another invalid payload """
        pl = self.get_payload_json()
        del pl['resources']['buckets']
        Payload(pl)

    def test_default_url(self):
        """ Get default url base """
        pl = self.get_payload_json()
        payload = Payload(pl)
        self.assertEqual(payload.default_url, 'https://cumulus.developmentseed.org/distribution/')
        del pl['resources']['distribution_endpoint']
        payload = Payload(pl)
        self.assertEqual(payload.default_url, 'https://cumulus.com')

    def test_default_urlpath(self):
        """ Get default url path """
        pl = self.get_payload_json()
        payload = Payload(pl)
        self.assertEqual(payload.default_urlpath, 'testing/cumulus-py')
        del pl['collection']['url_path']
        payload = Payload(pl)
        self.assertEqual(payload.default_urlpath, '')

    def test_urls(self):
        """ Get dictionary of regex keys with s3 and http urls """
        pl = self.get_payload_json()
        payload = Payload(pl)
        urls = payload.urls
        self.assertEqual(len(urls.keys()), 5)
        http = 'http://cumulus-internal.s3.amazonaws.com/testing/cumulus-py/testing/cumulus-py'
        self.assertEqual(urls['^output-1.txt$']['http'], http)
        http = 'https://cumulus.developmentseed.org/distribution/testing/cumulus-py/testing/cumulus-py'
        self.assertEqual(urls['^output-2.txt$']['http'], http)

    def test_output_files(self):
        """ Testing of output files """
        pl = self.get_payload_json()
        payload = Payload(pl)
        payload.add_output_granule(['output-1.txt', 'output-2.txt', 'output-3.meta.xml'])
        fnames = payload.filenames()
        self.assertEqual(len(fnames), 2)
        self.assertEqual(len(fnames[1]), 3)
