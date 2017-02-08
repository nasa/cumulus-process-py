#!/usr/bin/env python

import os
import logging
import boto3

from dotenv import load_dotenv, find_dotenv

# environment variables
load_dotenv(find_dotenv())
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

logger = logging.getLogger(__name__)


def s3_client():
    return boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


def uri_parser(uri):
    """ Split S3 URI into bucket, key, filename """
    if uri[0:5] != 's3://':
        raise Exception('Invalid S3 uri %s' % uri)

    uri_obj = uri.replace('s3://', '').split('/')

    return {
        'bucket': uri_obj[0],
        'key': '/'.join(uri_obj[1:]),
        'filename': uri_obj[-1]
    }


def download(uri, d='data/input'):
    """ Download object from S3 """
    s3 = s3_client()
    s3_obj = uri_parser(uri)

    with open(os.path.join(d, s3_obj['filename']), 'wb') as data:
        s3.download_fileobj(
            Bucket=s3_obj['bucket'],
            Key=s3_obj['key'],
            Fileobj=data
        )


def upload(filename, uri):
    """ Upload object to S3 uri (bucket + prefix), keeping same base filename """
    logger.debug("Uploading %s to %s" % (filename, uri))
    s3 = s3_client()
    s3_uri = uri_parser(uri)
    bname = os.path.basename(filename)
    uri_out = 's3://%s' % os.path.join(s3_uri['bucket'], os.path.join(s3_uri['key'], bname))
    with open(filename, 'rb') as data:
        s3.upload_fileobj(data, s3_uri['bucket'], os.path.join(s3_uri['key'], bname))
    return uri_out


def list(uri):
    """ Get list of objects within bucket and path """
    logger.debug("Listing contents of %s" % uri)
    s3 = s3_client()
    s3_uri = uri_parser(uri)
    response = s3.list_objects_v2(Bucket=s3_uri['bucket'], Prefix=s3_uri['key'])

    filenames = []
    if 'Contents' in response.keys():
        for file in response['Contents']:
            filenames.append(os.path.join('s3://%s' % s3_uri['bucket'], file['Key']))
    return filenames


def delete(uri):
    """ Remove an item from S3 """
    logger.debug('Deleting %s' % uri)
    s3 = s3_client()
    s3_uri = uri_parser(uri)
    # TODO - parse response and return success/failure
    try:
        res = s3.delete_object(Bucket=s3_uri['bucket'], Key=s3_uri['key'])
        return True
    except Exception as e:
        return False


def exists(uri):
    """ Check if this URI exists on S3 """
    logger.debug('Checking existence of %s' % uri)
    s3 = s3_client()
    s3_uri = uri_parser(uri)
    try:
        s3.get_object(Bucket=s3_uri['bucket'], Key=s3_uri['key'])
        return True
    except Exception as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return False
        else:
            raise
