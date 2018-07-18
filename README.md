# cumulus-process-py

[![CircleCI](https://circleci.com/gh/nasa/cumulus-process-py.svg?style=svg)](https://circleci.com/gh/nasa/cumulus-process-py)
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

## Testing

Testing requires [localstack](https://github.com/localstack/localstack). Follow the instruction for localstack and install it on your machine then:

    $ nosetests -v

## Usage

To use the library, subclass `Process` class from `cumulus_process` and implement:
1. the `process` method,
2. a `default_keys` property (needed for functionality such as `self.fetch()` unless you are overriding input_keys in config)

## Example:

See the [example](example) folder.