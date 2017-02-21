#!/usr/bin/env python

import argparse
import sys
import logging
from cumulus.version import __version__

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def parse_args(cls, args):
    """ Parse arguments for data processing """
    desc = '%s Processing' % cls.__name__
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)
    parser.add_argument('--version', help='Print version and exit', action='version', version=__version__)
    parser.add_argument('--recipe', help='Granule recipe (JSON, S3 address, or local file)', default=None)
    parser.add_argument('--path', help='Local working path', default='')
    parser.add_argument('--s3path', help='S3 prefix to save output', default=None)
    for f in cls.inputs:
        parser.add_argument(f.replace('-', ''), nargs='?', default=None)
    parser = cls.parser_args(parser)
    return parser.parse_args(args)


def cli(cls):
    """ Command Line Interface for a specific Granule class """
    args = parse_args(cls, sys.argv[1:])
    if args.recipe is not None:
        granule = cls(args.recipe, path=args.path, s3path=args.s3path)
        granule.run()
    else:
        cls.process(vars(args))
