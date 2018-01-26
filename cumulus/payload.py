import os
import json
import cumulus.s3 as s3
import logging

logger = logging.getLogger(__name__)


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

    def add_output_granule(self, gid, granule):
        """ Add output granules to the payload """
        # new files to add
        files = []
        for f in granule:
            uri = s3.uri_parser(f)
            files.append({
                'filename': f,
                'name': uri['filename'],
                'bucket': uri['bucket']
            })
        # check if granule already exists in payload, and add to it
        for g in self.payload['payload']['granules']:
            if gid == g['granuleId']:
                g['files'] += files
                return self.payload
        # otherwise, create new granule
        self.payload['payload']['granules'].append({'granuleId': gid, 'files': files})
        return self.payload
