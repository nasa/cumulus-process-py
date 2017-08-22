import os
import json
from cumulus.payload import Payload
import boto3
import traceback
from botocore.client import Config
from botocore.vendored.requests.exceptions import ReadTimeout
from cumulus.loggers import getLogger

logger = getLogger(__name__)

"""
cls is the Process subclass for a specific data source, such as MODIS, ASTER, etc.
"""

SFN_PAYLOAD_LIMIT = 32768


def lambda_handler(payload):
    """ Handler for AWS Lambda function """
    return run(payload)


def run(cls, payload, path='/tmp', noclean=False):
    """ Run this payload with the given Process class """
    pl = Payload(payload)
    granule = cls(pl.filenames(), path=path, url_paths=pl.urls)
    granule.run(noclean=noclean)
    for gran in granule.remote_out.values():
        pl.add_output_granule(gran.values())
    return pl.payload


def get_and_run_task(cls, sfn, arn):
    """ Get and run a single task as part of an activity """
    logger.info('query for task')
    try:
        task = sfn.get_activity_task(activityArn=arn, workerName=__name__)
    except ReadTimeout:
        logger.warning('Activity read timed out. Trying again.')
        return

    token = task.get('taskToken', None)
    if not token:
        logger.info('No activity task')
        return

    try:
        payload = json.loads(task['input'])
        # if need to get payload from s3
        #if 's3uri' in payload:
        #    payload = download_json(payload['s3uri'])

        # run job
        payload = run(cls, payload)

        # return sucess with result
        output = json.dumps(payload)
        # check payload size
        #if len(output) >= SFN_PAYLOAD_LIMIT:
        #    s3out = upload_result(result)
        #    output = json.dumps({'result': {'result_s3_uri': s3out}})

        sfn.send_task_success(taskToken=task['taskToken'], output=output)
    except Exception as e:
        tb = traceback.format_exc()
        sfn.send_task_failure(taskToken=task['taskToken'], error=str(e), cause=tb)


def activity(cls, arn=os.getenv('ACTIVITY_ARN')):
    """ An activity service for use with AWS Step Functions """
    sfn = boto3.client('stepfunctions', config=Config(read_timeout=70))
    while True:
        get_and_run_task(cls, sfn, arn)
