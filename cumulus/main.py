#!/usr/bin/env python

import os
import sys
import argparse
from cumulus.loggers import getLogger
from cumulus.version import __version__


def parse_args(cls, args):
    """ Parse arguments for data processing """
    desc = '%s Processing' % cls.__name__
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)
    parser.add_argument('--version', help='Print version and exit', action='version', version=__version__)
    parser.add_argument('--recipe', help='Granule recipe (JSON, S3 address, or local file)', default=None)
    parser.add_argument('--path', help='Local working path', default='')
    parser.add_argument('--s3path', help='S3 prefix to save output', default=None)
    parser.add_argument('--loglevel', help='0:all, 1:debug, 2:info, 3:warning, 4:error, 5:critical', default=1, type=int)
    parser.add_argument('--splunk', help='Splunk index name to log to splunk', default=None)
    for f in cls.inputs:
        parser.add_argument(f, nargs='?', default=None)
    parser = cls.parser_args(parser)
    return parser.parse_args(args)


def cli(cls):
    """ Command Line Interface for a specific Granule class """
    args = parse_args(cls, sys.argv[1:])

    splunk = args.splunk
    if splunk is not None:
        splunk = {
            'host': os.getenv('SPLUNK_HOST'),
            'user': os.getenv('SPLUNK_USERNAME'),
            'pass': os.getenv('SPLUNK_PASSWORD'),
            'port': os.getenv('SPLUNK_PORT', '8089'),
            'index': args.splunk,
            'level': args.loglevel * 10
        }

    logger = getLogger(__name__, splunk=splunk, stdout={'level': args.loglevel * 10})

    if args.recipe is not None:
        granule = cls(args.recipe, path=args.path, s3path=args.s3path, logger=logger)
        granule.run()
    else:
        cls.process(vars(args), path=args.path, logger=logger)
