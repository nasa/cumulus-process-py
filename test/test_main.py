"""
This testing module relies on some testing data available in s3://cumulus-internal/testing
"""

import os
import sys
from nose.tools import raises
from mock import patch, PropertyMock
import unittest
import logging
from cumulus.granule import Granule
from cumulus.main import parse_args, cli

# quiet these loggers
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)


class TestMain(unittest.TestCase):
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

    def test_parse_no_args(self):
        """ Parse arguments for CLI to a Granule class """
        args = parse_args(Granule, '')
        self.assertEqual(args.path, '')
        self.assertEqual(args.recipe, None)
        self.assertEqual(args.s3path, None)

    @raises(SystemExit)
    def test_parse_args_version(self):
        """ Parse version arguments """
        parse_args(Granule, ['--version'])

    def test_parse_args_recipe(self):
        """ Parse arguments given input files """
        cmd = '--recipe test/payload.json --path test/ --s3path s3://nosuchbucket'
        args = parse_args(Granule, cmd.split(' '))
        self.assertEqual(args.recipe, 'test/payload.json')
        self.assertEqual(args.path, 'test/')
        self.assertEqual(args.s3path, 's3://nosuchbucket')

    @patch('cumulus.granule.Granule.inputs', new_callable=PropertyMock)
    def test_parse_args(self, mocked_inputs):
        """ Test argument parsing """
        mocked_inputs.return_value = ['test-1', 'test-2']
        cmd = 'test-1.txt test-2.txt'
        args = vars(parse_args(Granule, cmd.split(' ')))
        self.assertEqual(args['test-1'], 'test-1.txt')
        self.assertEqual(args['test-2'], 'test-2.txt')

    def test_cli_recipe(self):
        """ Test CLI function with a recipe """
        sys.argv = ('program --recipe test/payload.json --path %s --loglevel 5' % (self.testdir)).split(' ')
        try:
            cli(Granule)
            assert False
        except IOError as e:
            self.assertEqual(e.message, 'Local output files do not exist')
        for f in ['input-1', 'input-2']:
            os.remove(os.path.join(self.testdir, f + '.txt'))

    @patch('cumulus.granule.Granule.inputs', new_callable=PropertyMock)
    def test_cli(self, mocked_inputs):
        """ Test CLI function without recipe """
        mocked_inputs.return_value = ['test-1', 'test-2']
        sys.argv = ('test1.txt test-2.txt --path %s' % self.testdir).split(' ')
        cli(Granule)
