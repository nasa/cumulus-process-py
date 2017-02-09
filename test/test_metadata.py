import os
import unittest
from cumulus.metadata import write_metadata


class TestMetadata(unittest.TestCase):
    """ Test metadata generation module """

    def test_write_metadata(self):
        """ Write metadata into file """
        fout = write_metadata('dummy.txt', dataname='data', dataid='placeholder_short_name')
        self.assertTrue(os.path.exists(fout))
