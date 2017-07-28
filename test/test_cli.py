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
from cumulus.cli import parse_args, cli


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

    @raises(SystemExit)
    def test_parse_no_args(self):
        """ Parse arguments for CLI to a Granule class """
        parse_args(Granule, '')

    @raises(SystemExit)
    def test_parse_args_version(self):
        """ Parse version arguments """
        parse_args(Granule, ['--version'])

    def test_parse_args_recipe(self):
        """ Parse arguments given input files """
        cmd = 'recipe test/payload.json --path test/ --noclean'
        args = parse_args(Granule, cmd.split(' '))
        self.assertEqual(args['recipe'], 'test/payload.json')
        self.assertEqual(args['path'], 'test/')
        self.assertEqual(args['noclean'], True)

    #@patch('cumulus.granule.Granule.inputs', new_callable=PropertyMock)
    def test_parse_args(self): #, mocked_inputs):
        """ Test argument parsing """
        #mocked_inputs.return_value = ['test-1', 'test-2']
        cmd = 'process test-1.txt test-2.txt'
        args = parse_args(Granule, cmd.split(' '))
        self.assertEqual(args['filenames'], ['test-1.txt', 'test-2.txt'])

    def test_cli_recipe(self):
        """ Test CLI function with a recipe """
        sys.argv = ('program recipe test/payload.json --path %s --loglevel 5' % (self.testdir)).split(' ')
        cli(Granule)
        for f in ['input-1', 'input-2']:
            fname = os.path.join(self.testdir, f + '.txt')
            self.assertFalse(os.path.exists(fname))

    #@patch('cumulus.granule.Granule.inputs', new_callable=PropertyMock)
    def test_cli(self): #, mocked_inputs):
        """ Test CLI function without recipe """
        #mocked_inputs.return_value = ['test-1', 'test-2']
        sys.argv = ('program process test-1.txt test-2.txt --path %s' % self.testdir).split(' ')
        cli(Granule)
