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
    payload = os.path.join(os.path.dirname(__file__), 'payload.json')
    path = os.path.dirname(__file__)
    s3path = 's3://%s/testing/cumulus-py' % bucket

    def uri(self, key):
        return 's3://%s' % os.path.join(self.bucket, key)

    def test_uri_parser(self):
        """ Parse S3 URI """
        s3_obj = s3.uri_parser(os.path.join(self.s3path, 'file.txt'))
        self.assertEqual(s3_obj['bucket'], self.bucket)
        self.assertEqual(s3_obj['key'], 'testing/cumulus-py/file.txt')
        self.assertEqual(s3_obj['filename'], 'file.txt')

    def test_not_exists(self):
        """ Check for existence of fake object """
        self.assertFalse(s3.exists(os.path.join(self.s3path, 'nosuchkey')))

    def test_list_nothing(self):
        """ Get list of objects under a non-existent path on S3 """
        uris = s3.list(os.path.join(self.s3path, 'nosuchkey'))
        self.assertEqual(len(uris), 0)

    def test_upload_and_delete(self):
        """ Upload file to S3 then delete """
        uri = s3.upload(__file__, self.s3path)
        self.assertTrue(s3.exists(uri))
        self.assertTrue(s3.delete(uri))
        self.assertFalse(s3.exists(uri))

    def test_download(self):
        """ Download file from S3 """
        fout = os.path.join(self.path, 'input-1.txt')
        with open(fout, 'w') as f:
            f.write('testing cumulus-py')
        uri = s3.upload(fout, self.s3path)
        os.remove(fout)
        self.assertFalse(os.path.exists(fout))
        f = s3.download(uri, path=self.path)
        self.assertEqual(f, fout)
        self.assertTrue(os.path.exists(f))
        os.remove(f)

    def test_download_as_text(self):
        """ Download file from S3 as JSON """
        uri = s3.upload(self.payload, self.s3path)
        record = s3.download_json(uri)
        self.assertTrue('granuleRecord' in record.keys())
        s3.delete(uri)
