import os
import uuid
import json
import unittest
import logging
from cumulus_process import s3

# quiet these loggers
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)

if not os.getenv('LOCALSTACK_HOST'):
    raise Exception('LOCALSTACK_HOST must be set as env variable before running tests')

class Test(unittest.TestCase):
    """ Test utilities for publishing data on AWS PDS """

    bucket = str(uuid.uuid4()) 
    payload = os.path.join(os.path.dirname(__file__), 'payload.json')
    path = os.path.dirname(__file__)
    s3path = 's3://%s/test' % bucket

    @classmethod
    def setUpClass(cls):
        cls.s3 = s3.get_client()
        cls.s3.create_bucket(Bucket=cls.bucket)

    @classmethod
    def tearDownClass(cls):
        cls.s3.delete_bucket(Bucket=cls.bucket)

    def uri(self, key):
        return 's3://%s' % os.path.join(self.bucket, key)

    def test_uri_parser(self):
        """ Parse S3 URI """
        s3_obj = s3.uri_parser(os.path.join(self.s3path, 'file.txt'))
        self.assertEqual(s3_obj['bucket'], self.bucket)
        self.assertEqual(s3_obj['key'], 'test/file.txt')
        self.assertEqual(s3_obj['filename'], 'file.txt')

    def test_exists_true(self):
        """ Check for existence of object that exists """

        uri = self.s3path + '/arealkey'
        s3.upload(self.payload, uri)
        self.assertTrue(s3.exists(uri))
        s3.delete(uri)

    def test_exists_false(self):
        """ Check for existence of object that doesn't exists """
        self.assertFalse(s3.exists(os.path.join(self.s3path, 'nosuchkey')))

    def test_list_nothing(self):
        """ Get list of objects under a non-existent path on S3 """
        uris = s3.list_objects(os.path.join(self.s3path, 'nosuchkey'))
        self.assertEqual(len(uris), 0)

    def test_upload(self):
        """ Upload file to S3 then delete """
        filename = os.path.basename(__file__)
        s3_uri = os.path.join(self.s3path, filename)
        uri = s3.upload(__file__, s3_uri)
        self.assertEqual(uri, s3_uri)
        s3.delete(s3_uri)

    def test_download(self):
        """ Download file from S3 """
        # first upload something
        uri = self.s3path + '/file.txt'
        s3.upload(self.payload, uri)

        fout = s3.download(uri, path=self.path)
        self.assertEqual(fout, os.path.join(self.path, 'file.txt'))
        s3.delete(uri)
        os.remove(fout)

    def test_download_json(self):
        """ Download file from S3 as JSON """
        json_obj = {
            'Body': {
                'this': 'that'
            }
        }
        self.s3.put_object(Bucket=self.bucket, Key='prefix/test.json', Body=json.dumps(json_obj))

        out = s3.download_json('s3://%s/prefix/test.json' % self.bucket)
        self.assertEqual(out, json_obj)
        s3.delete('s3://%s/prefix/test.json' % self.bucket)
