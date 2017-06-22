import os
import json
import cumulus.s3 as s3


def check_payload(payload):
    """ Test validity of payload """
    try:
        assert('granuleRecord' in payload)
        assert('recipe' in payload['granuleRecord'])
        assert('files' in payload['granuleRecord'])
        assert('processStep' in payload['granuleRecord']['recipe'])
        assert('config' in payload['granuleRecord']['recipe']['processStep'])
    except:
        raise ValueError("Invalid payload")


def parse_payload(payload):
    """ Process an input payload that is a file, a json string, or s3 location """
    if isinstance(payload, str):
        if payload[0:5] == 's3://':
            # s3 location
            payload = s3.download_json(payload)
        else:
            if os.path.exists(payload):
                with open(payload, 'r') as f:
                    payload = json.loads(f.read())
            else:
                try:
                    payload = json.loads(payload)
                except:
                    raise ValueError("Invalid payload: %s" % payload)
    check_payload(payload)
    record = payload['granuleRecord']
    filenames = [record['files'][r]['stagingFile'] for r in record['recipe']['processStep']['config']['inputFiles']]

    return {
        'gid': payload['granuleRecord']['granuleId'],
        'collection': payload['granuleRecord']['collectionName'],
        'filenames': filenames
    }
    return payload
