import json
import os
import time
import unittest
import uuid

import requests
from splunk_handler import SplunkHandler

from cumulus.logutils import get_logger, make_log_string


class TestLogutils(unittest.TestCase):
    ''' Test customized logging module '''

    def test_writing_to_splunk(self):
        ''' Integration test to confirm Splunk writing successful '''
        test_uuid = str(uuid.uuid4())

        # Write a record to the `integration_testing` index
        os.environ['SPLUNK_INDEX'] = 'integration_testing'
        logger = get_logger()
        logger.info('test_name="test_logutils" test_uuid="{}"'.format(test_uuid))

        # Wait a tiny bit for Splunk to ingest the record
        time.sleep(2)

        # Check whether it was posted to the Splunk
        response = requests.post(
            'https://{host}:{port}/servicesNS/admin/search/search/jobs/export'.format(
                host=os.environ['SPLUNK_HOST'],
                port=os.environ.get('SPLUNK_PORT', '8089')
            ),
            auth=(os.environ['SPLUNK_USERNAME'], os.environ['SPLUNK_PASSWORD']),
            params={'output_mode': 'json'},
            data={'search': 'search index="integration_testing" test_name="test_logutils" earliest="-1h" test_uuid="{}"'.format(test_uuid)},
            verify=False
        )

        # Parse the response, where each line is a JSON object describing a record,
        # and the final line is an EOF-ish object
        results = [json.loads(result) for result in response.content.split('\n') if result != '']
        import pprint; pprint.pprint(results)
        self.assertTrue('result' in results[0].keys())
        self.assertTrue(
            'result' not in results[1].keys() and
            results[1]['lastrow'] is True
        )

    def test_no_splunk_without_creds(self):
        ''' Check that no handler is added if Splunk credentials aren't found ''' 
        host = os.environ.pop('SPLUNK_HOST')
        logger = get_logger()
        os.environ['SPLUNK_HOST'] = host
        # Should have just a Nose memory handler and a StreamHandler
        self.assertTrue(not any(isinstance(logger_, SplunkHandler) for logger_ in logger.handlers))
