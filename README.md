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

Example:

```python
from cumulus_process import Process

class MyClass(Process):

  def process(self):
    print('Hello World Implementation');

```

## Cumulus Message Config
Example Cumulus Message input:

```json
{
  "config": {
    "granuleIdExtraction": "(.+?)\\.[^.]*$|$",
    "files_config": [
    {
        "regex": "^input-1.txt$",
        "bucket": "public"
    },
    {
        "regex": "^input-2.txt$",
        "bucket": "private"
    },
    {
        "regex": "^output-1.txt$",
        "bucket": "public"
    },
    {
        "regex": "^output-2.txt$",
        "bucket": "private"
    },
    {
        "regex": "^output-3.cmr.xml$",
        "bucket": "public",
        "url_path": "testing/cumulus-py/otherfolder"
    }],
    "url_path": "testing/cumulus-py",
    "buckets": {
      "internal": "cumulus",
      "private": "cumulus",
      "public": "cumulus",
      "protected": "cumulus"
    },
    "distribution_endpoint": "https://cumulus..com",
    "input_keys": {
      "input-1": "^.*-1.txt$",
      "input-2": "^.*-2.txt$"
    }
  },
  "input": [
    "s3://cumulus/testing/cumulus-py/input-1.txt",
    "s3://cumulus/testing/cumulus-py/input-2.txt"
  ]
}
```

### Fields
| field | rqeuired | description
| ----- | -------  | -----------
| config.granuleIdExtraction | Y |the regex used for extracting GranuleId from input filenames
| config.files_config | Y |list of file configurations. Each object in the list must include `regex` and `bucket`
| config.url_path | N | the folder to upload the generated files to
| config.buckets | Y | an object of buckets referenced in the files_config
| config.distribution_endpoint | N | the endpoint to use when generating CMR metadata
| input | Y | list of S3 uris


**Note:** The class expects to receive a list of S3 Uris

