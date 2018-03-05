import os
import json
import boto3
import traceback
from botocore.client import Config
from botocore.vendored.requests.exceptions import ReadTimeout
from cumulus_process.loggers import getLogger

logger = getLogger(__name__)

"""
cls is the Process subclass for a specific data source, such as MODIS, ASTER, etc.
"""

SFN_PAYLOAD_LIMIT = 32768


def activity(handler, arn=os.getenv('ACTIVITY_ARN')):
    """ An activity service for use with AWS Step Functions """
    sfn = boto3.client('stepfunctions', config=Config(read_timeout=70))
    while True:
        get_and_run_task(handler, sfn, arn)


def get_and_run_task(handler, sfn, arn):
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

        output = json.dumps(handler(event=payload))

        # check payload size
        #if len(output) >= SFN_PAYLOAD_LIMIT:
        #    s3out = upload_result(result)
        #    output = json.dumps({'result': {'result_s3_uri': s3out}})

        sfn.send_task_success(taskToken=task['taskToken'], output=output)
    except MemoryError as e:
        logger.error("Memory error when running task: %s" % str(e))
        tb = traceback.format_exc()
        sfn.send_task_failure(taskToken=task['taskToken'], error=str(e), cause=tb)
        raise e
    except Exception as e:
        tb = traceback.format_exc()
        sfn.send_task_failure(taskToken=task['taskToken'], error=str(e), cause=tb)
