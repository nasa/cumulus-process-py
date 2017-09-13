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

    @classmethod
    def validate(cls, payload):
        """ Test validity of payload """
        try:
            assert('resources' in payload)
            assert('buckets' in payload['resources'])
            assert('collection' in payload)
            assert('files' in payload['collection']['meta'])
            assert('payload' in payload)
            assert('granules' in payload['payload'])
        except Exception as e:
            logger.error(str(e))
            raise ValueError("Invalid payload")

    def filenames(self):
        """ Get input filenames """
        granules = self.payload['payload']['granules']
        filenames = []
        for g in granules:
            filenames.append([f['filename'] for f in g['files']])
        return filenames

    @property
    def default_url(self):
        """ Get default endpoint """
        default = 'https://cumulus.com'
        return self.payload['resources'].get('distribution_endpoint', default)

    @property
    def default_urlpath(self):
        """ Get default s3 path """
        return self.payload['collection']['meta'].get('url_path', '')

    @property
    def urls(self):
        """ Get dictionary of regex keys with s3 and http urls """
        files = self.payload['collection']['meta']['files']
        buckets = self.payload['resources']['buckets']
        urls = {}
        for f in files:
            url_path = f.get('url_path', self.default_urlpath)
            access = f.get('bucket', 'public')
            if access == 'public':
                http = 'http://%s.s3.amazonaws.com' % buckets[access]
            else:
                http = self.default_url
            http = os.path.join(http, url_path)
            urls[f['regex']] = {
                'access': access,
                's3': os.path.join('s3://%s' % buckets[access], url_path),
                'http': os.path.join(http, url_path)
            }
        return urls

    @property
    def gid_regex(self):
        return self.payload['collection']['meta'].get('granuleIdExtraction', None)

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
