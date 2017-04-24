#!/usr/bin/env python

from cumulus.main import cli as cumulus_cli
from cumulus_dataname import DATANAME


def cli():
    cumulus_cli(DATANAME)


if __name__ == "__main__":
    cli()
