import os
import unittest
import logging
import cumulus.s3 as s3

# quiet these loggers
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)


class TestS3(unittest.TestCase):
    """ Test utiltiies for publishing data on AWS PDS """

    bucket = 'cumulus-internal'

    def uri(self, key):
        return 's3://%s' % os.path.join(self.bucket, key)

    def test_uri_parser(self):
        """ Parse S3 URI """
        key = 'testing/file.txt'
        s3_obj = s3.uri_parser(self.uri(key))
        self.assertEqual(s3_obj['bucket'], self.bucket)
        self.assertEqual(s3_obj['key'], key)
        self.assertEqual(s3_obj['filename'], 'file.txt')

    def test_not_exists(self):
        """ Check for existence of fake object """
        self.assertFalse(s3.exists(self.uri('nosuchkey')))

    def test_list_nothing(self):
        """ Get list of objects under a non-existent path on S3 """
        uris = s3.list(self.uri('nosuchkey'))
        self.assertEqual(len(uris), 0)

    def test_list(self):
        """ Get list of objects under a path on S3 """
        uri = s3.upload(__file__, self.uri('testing'))
        fnames = s3.list(os.path.dirname(uri))
        self.assertEqual(len(fnames), 1)
        self.assertEqual(fnames[0], uri)
        s3.delete(uri)

    def test_upload_and_delete(self):
        """ Upload file to S3 then delete """
        uri = s3.upload(__file__, self.uri('testing'))
        self.assertTrue(s3.exists(uri))
        self.assertTrue(s3.delete(uri))
        self.assertFalse(s3.exists(uri))
