# cumulus-process-py

[![CircleCI](https://circleci.com/gh/cumulus-nasa/cumulus-process-py.svg?style=svg&circle-token=6564d296f06c4d8d2925e220c4a213267dc70c00)](https://circleci.com/gh/cumulus-nasa/cumulus-process-py)
[![PyPI version](https://badge.fury.io/py/cumulus-process.svg)](https://badge.fury.io/py/cumulus-process)

cumulus-process-py is a collection of python utilities for the NASA Cumulus project.

## The Use Case

This library provides various utilities and helper functions for python tasks developed to work with the Cumulus framework.

The utilities help writing tasks that involve metadata extraction from input files, thumbnail creation, or even more complex data processing such as running custom science code to create higher level products from an input file.

## Installation

    $ pip install cumulus-process

## Development

    $ pip install -r requirements.txt
    $ pip install -r requirements-dev.txt

To test:

    $ nosetests -v

## Usage

To use the library, subclass `Process` class from `cumulus_process` and implement:
1. the `process` method,
2. a `default_keys` property (needed for functionality such as `self.fetch()` unless you are overriding input_keys in config)

## Example:

See the [example](example) folder.