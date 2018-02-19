import os
import unittest
import logging
import cumulus_process.s3 as s3
try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

# quiet these loggers
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)


class Test(unittest.TestCase):
    """ Test utiltiies for publishing data on AWS PDS """

    bucket = 'cumulus-py'
    payload = os.path.join(os.path.dirname(__file__), 'payload.json')
    path = os.path.dirname(__file__)
    s3path = 's3://%s/test' % bucket

    def uri(self, key):
        return 's3://%s' % os.path.join(self.bucket, key)

    def test_uri_parser(self):
        """ Parse S3 URI """
        s3_obj = s3.uri_parser(os.path.join(self.s3path, 'file.txt'))
        self.assertEqual(s3_obj['bucket'], self.bucket)
        self.assertEqual(s3_obj['key'], 'test/file.txt')
        self.assertEqual(s3_obj['filename'], 'file.txt')

    @patch('cumulus_process.s3.boto3')
    def test_exists_true(self, boto3):
        """ Check for existence of object that exists """
        self.assertTrue(s3.exists(os.path.join(self.s3path, 'arealkey')))

    @patch('cumulus_process.s3.boto3')
    def test_exists_false(self, boto3):
        """ Check for existence of object that doesn't exists """
        class err(Exception):
            response = {'Error': {'Code': 'NoSuchKey'}}
        boto3.client().get_object.side_effect = err()
        self.assertFalse(s3.exists(os.path.join(self.s3path, 'nosuchkey')))

    @patch('cumulus_process.s3.boto3')
    def test_list_nothing(self, boto3):
        """ Get list of objects under a non-existent path on S3 """
        uris = s3.list_objects(os.path.join(self.s3path, 'nosuchkey'))
        self.assertEqual(len(uris), 0)

    @patch('cumulus_process.s3.boto3')
    def test_upload(self, boto3):
        """ Upload file to S3 then delete """
        filename = os.path.basename(__file__)
        s3_uri = os.path.join(self.s3path, filename)
        uri = s3.upload(__file__, s3_uri)
        self.assertEqual(uri, s3_uri)
        self.assertTrue(boto3.client().upload_fileobj.called)

    @patch('cumulus_process.s3.boto3')
    def test_download(self, boto3):
        """ Download file from S3 """
        fout = s3.download('s3://test/file.txt', path=self.path)
        self.assertEqual(fout, os.path.join(self.path, 'file.txt'))
        boto3.client.assert_called_with('s3')
        self.assertTrue(boto3.client().download_fileobj.called)

    @patch('cumulus_process.s3.boto3')
    def _test_download_json(self, boto3):
        """ Download file from S3 as JSON """
        boto3.client().get_object().read.return_value = "{'Body': '{}''}"
        out = s3.download_json('s3://bucket/prefix/test.json')
        self.assertEqual(out, {})
        self.assertTrue(boto3.client().get_object.called)
        boto3.client().get_object.called_with('bucket', 'prefix/test.json')
