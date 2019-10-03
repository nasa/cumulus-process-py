#!/usr/bin/env python

import os
import json
import logging
import boto3

logger = logging.getLogger(__name__)


def get_client(client='s3'):
    """ creates and return a boto3 (aws) client """
    local_stack_ports = { 
        'apigateway': 4567,
        'cloudformation': 4581,
        'cloudwatch': 4582,
        'cloudwatchevents': 4582,
        'dynamodb': 4569,
        'dynamodbstreams': 4570,
        'es': 4571,
        'firehose': 4573,
        'kinesis': 4568,
        'lambda': 4574,
        'redshift': 4577,
        'route53': 4580,
        's3': 4572,
        'ses': 4579,
        'sns': 4575,
        'sqs': 4576,
        'ssm': 4583
    }

    localstack = os.getenv('LOCALSTACK_HOST')
    if localstack:
        return boto3.client(
            client,
            region_name='us-east-1',
            endpoint_url='http://%s:%s' % (localstack, local_stack_ports[client]),
            use_ssl=False,
            aws_access_key_id='fake-key',
            aws_secret_access_key='fake-secret'
        )

    return boto3.client(client)


def uri_parser(uri):
    """ Split S3 URI into bucket, key, filename """
    if uri[0:5] != 's3://':
        raise Exception('Invalid S3 uri %s' % uri)

    uri_obj = uri.replace('s3://', '').split('/')

    # remove empty items
    uri_obj = list(filter(lambda x: x, uri_obj))

    return {
        'bucket': uri_obj[0],
        'key': '/'.join(uri_obj[1:]),
        'filename': uri_obj[-1]
    }


def mkdirp(path):
    """ Recursively make directory """
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def download(uri, path=''):
    """ Download object from S3 """
    s3_uri = uri_parser(uri)
    fout = os.path.join(path, s3_uri['filename'])
    logger.debug("Downloading %s as %s" % (uri, fout))
    if path != '':
        mkdirp(path)

    s3 = get_client()

    with open(fout, 'wb') as f:
        s3.download_fileobj(
            Bucket=s3_uri['bucket'],
            Key=s3_uri['key'],
            Fileobj=f
        )
    return fout


def download_json(uri):
    """ Download object from S3 as JSON """
    logger.debug("Downloading %s as JSON" % (uri))
    s3 = get_client()
    s3_uri = uri_parser(uri)
    response = s3.get_object(Bucket=s3_uri['bucket'], Key=s3_uri['key'])
    return json.loads(response['Body'].read().decode())


def upload(filename, uri, extra={}):
    """ Upload object to S3 uri (bucket + prefix), keeping same base filename """
    logger.debug("Uploading %s to %s" % (filename, uri))
    s3 = get_client()
    s3_uri = uri_parser(uri)
    uri_out = 's3://%s' % os.path.join(s3_uri['bucket'], s3_uri['key'])
    with open(filename, 'rb') as data:
        s3.upload_fileobj(data, s3_uri['bucket'], s3_uri['key'], ExtraArgs=extra)
    return uri_out


def list_objects(uri):
    """ Get list of objects within bucket and path """
    logger.debug("Listing contents of %s" % uri)
    s3 = get_client()
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
    s3 = get_client()
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
    s3 = get_client()
    s3_uri = uri_parser(uri)
    try:
        s3.get_object(Bucket=s3_uri['bucket'], Key=s3_uri['key'])
        return True
    except Exception as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return False
        else:
            raise
