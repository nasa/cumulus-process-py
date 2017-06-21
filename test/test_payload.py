import os
import unittest
from cumulus.payload import process_payload


class TestPayload(unittest.TestCase):
    """ Test utiltiies for publishing data on AWS PDS """

    bucket = 'cumulus-internal'
    testdir = os.path.dirname(__file__)
    payload = os.path.join(testdir, 'payload.json')

    def test_parse_payload_file(self):
        """ Parse test payload """
        payload = process_payload(self.payload)
        self.assertTrue('gid' in payload)
        self.assertEqual(len(payload['filenames']), 2)
