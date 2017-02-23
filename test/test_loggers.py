
import os
import logging
import time
import unittest
import uuid
from ast import literal_eval
from testfixtures import log_capture, compare, Comparison as C, should_raise
from cumulus.loggers import getLogger, get_splunk_logs
from dotenv import load_dotenv

# load envvars
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)


class TestLoggers(unittest.TestCase):
    ''' Test Cumulus logger '''

    def test_config(self):
        """ Check configuration of logger """
        # null handler
        logger = getLogger(__name__)
        compare([
            C('logging.NullHandler')
            ], logger.handlers)
        # stdout handler
        logger = getLogger(__name__, stdout={'level': logging.INFO})
        compare([
            C('logging.StreamHandler', level=logging.INFO, strict=False)
            ], logger.handlers)

    def test_splunk_config(self):
        """ Configure splunk handler """
        # just use blank creds, they are not validated when creating logger
        splunk = {'host': '', 'user': '', 'pass': '', 'level': logging.INFO}
        # splunk handler
        logger = getLogger(__name__, splunk=splunk)
        compare([
            C('splunk_handler.SplunkHandler', level=logging.INFO, strict=False)
            ], logger.handlers)

    @should_raise(RuntimeError('Splunk logging requires host, user, and pass fields'))
    def test_splunk_config_no_creds(self):
        """ Attempt config of splunk handler without creds """
        getLogger(__name__, splunk={})

    @log_capture()
    def test_logger(self, lc):
        """ Stream logger """
        logger = getLogger(__name__, stdout={'level': logging.INFO})
        logger.info('test message')
        vals = [v for v in lc.actual()][0]
        self.assertEqual(vals[0], __name__)
        self.assertEqual(vals[1], 'INFO')
        d = literal_eval(vals[2])
        self.assertEqual(d['message'], 'test message')

    @log_capture()
    def test_logger_json(self, lc):
        """ Stream logger with JSON output """
        logger = getLogger(__name__, stdout={'level': logging.INFO})
        logger = logging.LoggerAdapter(logger, {'collectionName': 'test_collection'})
        logger.info({'key1': 'val1', 'key2': 'val2'})
        vals = [v for v in lc.actual()][0]
        self.assertEqual(vals[0], __name__)
        self.assertEqual(vals[1], 'INFO')
        d = literal_eval(vals[2])
        self.assertTrue('collectionName' in d.keys())
        self.assertTrue('timestamp' in d.keys())
        self.assertEqual(d['message'], '')
        self.assertEqual(d['key1'], 'val1')

    def test_splunk_logger(self):
        ''' Write log to splunk and read back '''

        splunk = {
            'host': os.getenv('SPLUNK_HOST'),
            'user': os.getenv('SPLUNK_USERNAME'),
            'pass': os.getenv('SPLUNK_PASSWORD'),
            'port': os.getenv('SPLUNK_PORT', '8089'),
            'index': 'integration_testing',
            'level': logging.INFO
        }

        testname = self.test_splunk_logger.__name__
        gid = str(uuid.uuid4())
        logger = getLogger(__name__, splunk=splunk)
        logger = logging.LoggerAdapter(logger, {'collectionName': gid})

        # Write a record to the `integration_testing` index
        logger.info({'message': 'testmessage', 'test': testname, 'granuleId': gid})

        # Wait a tiny bit for Splunk to ingest the record
        time.sleep(3)

        logs = get_splunk_logs(config=splunk, granuleId=gid, test=testname, earliest='-1h')
        self.assertEqual(logs[0]['granuleId'], gid)
        self.assertEqual(logs[0]['test'], testname)
