import os
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
            assert('resources' in payload)
            assert('meta' in payload)
            assert('collections' in payload['meta'])
            assert('payload' in payload)
            assert('buckets' in payload['resources'])
        except:
            raise ValueError("Invalid payload")

    @property
    def collections(self):
        """ Get list of collections referenced in payload """
        return self.payload['meta']['collections'].keys()

    def input_filenames(self):
        """ Get parameters used for processing the granule """
        inputs = self.payload['payload']['input']
        filenames = []
        for c in inputs:
            for g in inputs[c]['granules']:
                filenames += g['files'].values()
        return filenames

    def visibility(self, collection=None):
        vis = {}
        for c in self.collections:
            files = self.payload['meta']['collections'][c]['files']
            vis.update({k: files[k].get('access', 'public') for k in files})
        return vis

    def s3paths(self):
        """ Get dictionary of buckets based on access """
        buckets = self.payload['resources']['buckets']
        for b in buckets:
            buckets[b] = 's3://%s' % buckets[b]
        return buckets

    def add_output_files(self, granules, collection=None):
        """ Add output granules to the payload """
        if collection is None:
            collection = self.collections[0]

        self.payload['payload']['output'][collection]['granules'] += granules

        return self.payload
        # match output with regex
        #for c in collections:
        #    keys = self.payload['collections'][c]['files'].keys()
        #    for k in keys:
        #        pattern = self.payload['collections'][c]['files'][k]['regex']
        #        for f in filenames:
        #            m = re.match(pattern, os.path.basename(f))
        #            if m is not None:
        #                self.payload['payload']['outputs'][c]['granules'][k]['stagingFile'] = f
        #return self.payload
