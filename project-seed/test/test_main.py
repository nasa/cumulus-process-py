import os
import logging
import unittest

# quiet these loggers
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
logging.getLogger('dicttoxml').setLevel(logging.CRITICAL)


class TestMain(unittest.TestCase):
    """ Testing class for testing process outputs """

    testdir = os.path.dirname(__file__)
    payload = os.path.join(testdir, 'payload.json')
    tests3 = 's3://cumulus-internal/testing/dataname'

    # no tests yet
