import os
import logging
import unittest
from cumulus_dataname import DATANAME

# quiet these loggers
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
logging.getLogger('dicttoxml').setLevel(logging.CRITICAL)


class TestData(unittest.TestCase):
    """ Testing class for testing process outputs """

    testdir = os.path.dirname(__file__)
    payloads = [
        os.path.join(testdir, 'payload_MYD13A1.json'),
        os.path.join(testdir, 'payload_MOD09GQ.json')
    ]
    tests3 = 's3://cumulus-internal/testing/dataname'

    def get_granule(self):
        """ Get a test ASTER class with test payload """
        return DATANAME(self.payloads[0], path=self.testdir, s3path=self.tests3)

    def test_init(self):
        """ Test initialization of class """
        gran = self.get_granule()
        self.assertEqual(gran.id, 'DATANAME_TESTGRANULE')

    def test_process_wrapper(self):
        """ Process files in Granule process wrapper (includes tests for input and output files) """
        gran = DATANAME(self.payloads[0], path=self.testdir, s3path=self.tests3)
        gran.download()
        # process recipe checks input and output exist
        gran.process_recipe()
        gran.clean()

    def test_process(self):
        """ Process input files """
        gran = self.get_granule()
        inputs = gran.download()
        output = DATANAME.process(inputs, path=self.testdir)
        # ones less than normal since this test only has 2 thumbnails rather than 3
        self.assertEqual(len(output), len(gran.output_files)-1)
        # check and clean up output files
        for f in output.values():
            self.assertTrue(os.path.exists(f))
            os.remove(f)
        gran.clean()
