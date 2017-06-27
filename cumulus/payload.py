import os
import re
import json
import cumulus.s3 as s3


class Payload(object):
    """ A payload object """

    def __init__(self, payload):
        """ Initialize payload object with payload JSON """
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
        self.validate(payload)
        self.payload = payload

    @classmethod
    def validate(cls, payload):
        """ Test validity of payload """
        try:
            assert('granuleRecord' in payload)
            assert('recipe' in payload['granuleRecord'])
            assert('files' in payload['granuleRecord'])
            assert('processStep' in payload['granuleRecord']['recipe'])
            assert('config' in payload['granuleRecord']['recipe']['processStep'])
        except:
            raise ValueError("Invalid payload")

    @property
    def output_keys(self):
        """ Get keys of output files """
        return self.payload['granuleRecord']['recipe']['processStep']['config']['outputFiles']

    def process_parameters(self):
        """ Get parameters used for processing the granule """
        record = self.payload['granuleRecord']
        filenames = [record['files'][r]['stagingFile'] for r in record['recipe']['processStep']['config']['inputFiles']]

        return {
            'gid': self.payload['granuleRecord']['granuleId'],
            'collection': self.payload['granuleRecord']['collectionName'],
            'filenames': filenames
        }

    def visibility(self):
        return {k: self.payload['granuleRecord']['files'][k].get('access', 'public') for k in self.output_keys}

    def add_output_files(self, filenames):
        keys = self.payload['granuleRecord']['recipe']['processStep']['config']['outputFiles']
        for k in keys:
            pattern = self.payload['granuleRecord']['files'][k]['regex']
            for f in filenames:
                m = re.match(pattern, os.path.basename(f))
                if m is not None:
                    self.payload['granuleRecord']['files'][k]['stagingFile'] = f
        return self.payload
