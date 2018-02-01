
import logging
import unittest
from ast import literal_eval
from testfixtures import log_capture, compare, Comparison as C
from cumulus_process.loggers import getLogger


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
