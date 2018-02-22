"""
This testing module relies on some testing data available in s3://cumulus-internal/testing
"""

import os
import sys
import unittest
from cumulus_process import Process
from cumulus_process.cli import parse_args, cli


class Test(unittest.TestCase):
    """ Test utiltiies for publishing data on AWS PDS """

    testdir = os.path.dirname(__file__)

    def create_output_files(self):
        """ Create test output files """
        fouts = {}
        for out in ['output-1', 'output-2']:
            fout = os.path.join(self.testdir, out + '.txt')
            with open(fout, 'w') as f:
                f.write(out)
            fouts[out] = fout
        return fouts

    def _test_parse_no_args(self):
        """ Parse arguments for CLI to a Granule class, this test fails in Python3 """
        with self.assertRaises(SystemExit) as context:
            parse_args(Process, '')

    def test_parse_args_version(self):
        """ Parse version arguments """
        with self.assertRaises(SystemExit) as context:
            parse_args(Process, ['--version'])

    def test_parse_args_payload(self):
        """ Parse arguments given input files """
        cmd = 'payload test/payload.json --path test/ --noclean'
        args = parse_args(Process, cmd.split(' '))
        self.assertEqual(args['payload'], 'test/payload.json')
        self.assertEqual(args['path'], 'test/')
        self.assertEqual(args['noclean'], True)

    def test_parse_args(self): #, mocked_inputs):
        """ Test argument parsing """
        cmd = 'process test-1.txt test-2.txt'
        args = parse_args(Process, cmd.split(' '))
        self.assertEqual(args['input'], ['test-1.txt', 'test-2.txt'])

    def _test_cli_payload(self):
        """ Test CLI function with a payload """
        pl = os.path.join(self.testdir, 'payload.json')
        sys.argv = ('program payload %s --path %s --loglevel 5' % (pl, (self.testdir))).split(' ')
        cli(Process)
        for f in ['input-1', 'input-2']:
            fname = os.path.join(self.testdir, f + '.txt')
            self.assertFalse(os.path.exists(fname))

    def test_cli(self):
        """ Test CLI function without payload """
        sys.argv = ('program process test-1.txt test-2.txt --path %s' % self.testdir).split(' ')
        cli(Process)
