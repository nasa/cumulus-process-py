import os
import unittest
from cumulus.metadata import write_metadata


class TestMetadata(unittest.TestCase):
    """ Test sat-util generic parser class """

    def test_write_metadata(self):
        """ Write metadata into file """
        fout = write_metadata('dummy.txt', dataname='data')
        self.assertTrue(os.path.exists(fout))


