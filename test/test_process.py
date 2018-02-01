"""
This testing module relies on some testing data available in s3://cumulus-internal/testing
"""

import os
import unittest
from mock import patch
import cumulus_process.s3 as s3
from cumulus_process import Process


# mocked function replaced Granule.process
def fake_process(self):
    """ Create local output files as if process did something """
    # produce one fake granu
    Test.create_files(Test.output_files.values())
    local_out = {}
    for f in Test.output_files:
        local_out[f] = Test.output_files[f]
    self.local_out['TestGranule'] = local_out


class _Test(unittest.TestCase):
    """ Test utiltiies for publishing data on AWS PDS """

    path = os.path.dirname(__file__)

    s3path = 's3://cumulus-internal/testing/cumulus-py'
    input_files = [
        os.path.join(s3path, "input-1.txt"),
        os.path.join(s3path, "input-2.txt")
    ]

    output_files = {
        'output-1': os.path.join(path, 'output-1.txt'),
        'output-2': os.path.join(path, 'output-2.txt'),
        'meta': os.path.join(path, 'output-3.meta.xml')
    }

    urls = {
        '.*': {
            's3': s3path,
            'http': 'http://cumulus.com/testing/cumulus-py'
        }
    }

    @classmethod
    def create_files(cls, filenames):
        """ Create small files for testing """
        fouts = []
        for fname in filenames:
            fout = os.path.join(cls.path, os.path.basename(fname))
            with open(fout, 'w') as f:
                f.write(fname)
            fouts.append(fout)
        return fouts

    @classmethod
    def setUpClass(cls):
        """ Put some input files up on S3 """
        fouts = cls.create_files(cls.input_files)
        for f in fouts:
            s3.upload(f, cls.s3path)
            os.remove(f)

    def get_test_process(self):
        """ Get Process class for testing """
        return Process(self.input_files, path=self.path, url_paths=self.urls)

    def test_init(self):
        """ Initialize Granule with JSON payload """
        granule = self.get_test_process()
        self.assertTrue(granule.gid, "test_granule")
        self.assertTrue(granule.remote_in['input-1'], self.input_files[0])
        self.assertTrue(granule.remote_in['input-2'], self.input_files[1])

    def test_write_metadata(self):
        """ Write an XML metadata file from a dictionary """
        fout = os.path.join(self.path, 'test_write_metadata.meta.xml')
        Process.write_metadata({'key1': 'val1'}, fout)
        self.assertTrue(os.path.exists(fout))
        os.remove(fout)

    def test_publish_public_files(self):
        """ Get files to publish + endpoint prefixes """
        granule = self.get_test_process()
        # add fake some remote output files
        granule.local_out['TestGranule'] = {
            'output-1': 'nowhere/output-1',
            'output-2': 'nowhere/output-2'
        }
        urls = granule.publish()
        self.assertEqual(urls[urls.keys()[0]]['output-1'], 'http://cumulus.com/testing/cumulus-py/output-1')

    @patch.object(Process, 'process', fake_process)
    def test_upload(self):
        """ Upload output files """
        granule = self.get_test_process()
        granule.process()
        uploads = granule.upload()
        self.assertEqual(len(uploads), 1)
        for u in uploads:
            self.check_and_remove_remote_out(u)
        granule.clean()
        self.assertFalse(os.path.exists(os.path.join(self.path, 'output-1.txt')))

    @patch.object(Process, 'process', fake_process)
    def test_run(self):
        """ Make complete run """
        granule = Process(self.input_files, path=self.path, url_paths=self.urls)
        granule.run(noclean=True)
        # check for local output files
        for f in self.output_files.values():
            self.assertTrue(os.path.exists(f))

        # check for remote files
        uris = [uri for f in granule.remote_out.values() for uri in f.values()]
        self.assertTrue(len(uris) > 1)
        self.check_and_remove_remote_out(uris)

        granule.clean()
        for f in self.output_files.values():
            self.assertFalse(os.path.exists(f))

    def _check_and_remove_remote_out(self, uris):
        """ Check for existence of remote files, then remove them """
        for uri in uris:
            self.assertTrue(s3.exists(uri))
            s3.delete(uri)
            self.assertFalse(s3.exists(uri))
