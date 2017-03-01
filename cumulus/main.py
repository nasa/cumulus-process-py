#!/usr/bin/env python

import os
import sys
import argparse
from cumulus.granule import Granule
from cumulus.loggers import getLogger
from cumulus.version import __version__


def parse_args(cls, args):
    """ Parse arguments for data processing """
    desc = '%s Processing' % cls.__name__
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser0 = argparse.ArgumentParser(description=desc)

    pparser = argparse.ArgumentParser(add_help=False)
    pparser.add_argument('--version', help='Print version and exit', action='version', version=__version__)
    pparser.add_argument('--path', help='Local working path', default='')
    pparser.add_argument('--loglevel', default=2, type=int,
                         help='0:all, 1:debug, 2:info, 3:warning, 4:error, 5:critical')

    subparsers = parser0.add_subparsers(dest='command')

    parser = subparsers.add_parser('process', parents=[pparser], help='Process local files', formatter_class=dhf)
    for f in cls.inputs:
        parser.add_argument(f, default=None)

    recipe_parser = subparsers.add_parser('recipe', parents=[pparser], help='Process recipe file', formatter_class=dhf)
    recipe_parser.add_argument('recipe', help='Granule recipe (JSON, S3 address, or local file)')
    recipe_parser.add_argument('--s3path', help='S3 prefix to save output', default=None)
    recipe_parser.add_argument('--noclean', action='store_true', default=False,
                               help='Do not remove local files when done')
    recipe_parser.add_argument('--dispatcher', help='Name of Dispatcher Lambda', default=None)
    parser0 = cls.add_parser_args(parser0)
    return parser0.parse_args(args)


def cli(cls):
    """ Command Line Interface for a specific Granule class """
    args = parse_args(cls, sys.argv[1:])

    if args.command == 'recipe':
        splunk = {
            'host': os.getenv('SPLUNK_HOST', ''),
            'user': os.getenv('SPLUNK_USERNAME', ''),
            'pass': os.getenv('SPLUNK_PASSWORD', ''),
            'port': os.getenv('SPLUNK_PORT', '8089'),
            'index': os.getenv('SPLUNK_INDEX', 'main'),
            'level': args.loglevel * 10
        }
        if splunk['host'] == '' or splunk['user'] == '' or splunk['pass'] == '':
            splunk = None
        if args.s3path is None:
            args.s3path = os.getenv('internal')
        logger = getLogger(__name__, splunk=splunk, stdout={'level': args.loglevel * 10})
        granule = cls(args.recipe, path=args.path, s3path=args.s3path, logger=logger)
        granule.run(noclean=args.noclean)
        if args.dispatcher is not None:
            granule.next()
    elif args.command == 'process':
        logger = getLogger(__name__, stdout={'level': args.loglevel * 10})
        cls.process(vars(args), path=args.path, logger=logger)


if __name__ == "__main__":
    cli(Granule)
