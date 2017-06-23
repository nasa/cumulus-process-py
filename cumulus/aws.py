import os
import json
import cumulus.s3 as s3
from cumulus.payload import parse_payload
import boto3
import traceback
from botocore.client import Config
from botocore.vendored.requests.exceptions import ReadTimeout
from cumulus.loggers import getLogger

logger = getLogger(__name__)


def lambda_handler(payload):
    """ Handler for AWS Lambda function """
    run(payload)


def run(cls, payload, path='/tmp', s3path='', noclean=False):
    """ Run this payload with the given Granule class """
    pl = parse_payload(payload)
    from nose.tools import set_trace; set_trace()
    granule = cls(pl['filenames'], gid=pl['gid'], collection=pl['collection'],
                  path=path, s3path=s3path)
    granule.run(noclean=noclean)
    return granule
    # update payload with output files


def get_and_run_task(cls, sfn, arn):
    """ Get and run a single task as part of an activity """
    logger.info('qury for task')
    try:
        task = sfn.get_activity_task(activityArn=arn, workerName=__name__)
    except ReadTimeout:
        logger.warning('Activity read timed out. Trying again.')
        return
    try:
        payload = json.loads(task['input'])
        # run job
        granule = run(cls, payload)
        # return sucess with result
        sfn.send_task_success(taskToken=task['taskToken'], output=json.dumps({'result': result}))
    except Exception as e:
        tb = traceback.format_exc()
        sfn.send_task_failure(taskToken=task['taskToken'], error=str(e), cause=tb)


def activity(cls):
    """ An activity service for use with AWS Step Functions """
    arn = os.getenv('ACTIVITY_ARN')
    sfn = boto3.client('stepfunctions', config=Config(read_timeout=70))
    while True:
        get_and_run_task(cls, sfn, arn)

