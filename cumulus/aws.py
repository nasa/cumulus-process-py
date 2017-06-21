import os
import json
import cumulus.s3 as s3
import boto3
from cumulus.loggers import getLogger

logger = getLogger(__name__)





def process(payload):
    gran = granule_from_payload(payload)
    gran.process()
    #payload['granuleRecord']['files'][f]['stagingFile'] = uri



def lambda_handler(payload):
    """ Handler for AWS Lambda function """
    pass


def run_task():
    """ Get and run a single task as part of an activity """


def activity():
    """ An activity service for use with AWS Step Functions """
    pass


def next(self, payload, lambda_name):
    """ Send payload to dispatcher lambda """
    # update payload
    try:
        payload['previousStep'] = self.payload['nextStep']
        payload['nextStep'] = self.payload['nextStep'] + 1
        # invoke dispatcher lambda
        s3.invoke_lambda(payload, lambda_name)
    except Exception as e:
        logger.error('Error sending to dispatcher lambda: %s' % str(e))