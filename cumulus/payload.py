import os
import json
import cumulus.s3 as s3


def check_payload(self):
    """ Test validity of payload """
    try:
        assert('granuleRecord' in self.payload)
        assert('recipe' in self.payload['granuleRecord'])
        assert('files' in self.payload['granuleRecord'])
        assert('processStep' in self.payload['granuleRecord']['recipe'])
        assert('config' in self.payload['granuleRecord']['recipe']['processStep'])
    except:
        raise ValueError("Invalid payload")


def process_payload(payload):
    """ Process an input payload that is a file, a json string, or s3 location """
    if isinstance(payload, str):
        if payload[0:5] == 's3://':
            # s3 location
            payload = s3.download_json(payload)
        else:
            if not os.path.exists(payload):
                raise ValueError("Payload file %s does not exist" % payload)
            with open(payload, 'r') as f:
                payload = json.loads(f.read())
    check_payload(payload)
    record = payload['granuleRecord']
    filenames = [record['files'][r]['stagingFile'] for r in record['recipe']['processStep']['config']['inputFiles']]
    return {
        'gid': payload['granuleRecord']['granuleId'],
        'collection': payload['granuleRecord']['collectionName'],
        'filenames': filenames
    }
    return payload
