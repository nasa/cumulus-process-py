# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## Unreleased


## [1.0.0] - 1/4/22

### BREAKING CHANGES

- **CUMULUS-2751**

  - Update Cumulus Message Adapter dependency to ~2.0.0
    - This is a breaking change as the underlying behavior of the message adapter has changed See Cumulus Message Adapter release notes for more information.   This update *requires* an update of all Core tasks to use CMA v2.0.0 for message consistency reasons
  - Update boto3 dependency to ~1.18.40

## [0.10.0] - 5/21/21

- Remove `public-read` ACL from S3 object uploads to comply with NGAP access requirements.
- Update minimum dependency versions:
  - boto3:       1.4 -> 1.12.47
  - dicttoxml:   1.7 -> 1.7.4
  - cumulus-message-adapter-python: 1.2.0. -> 1.2.1
- Update minimum dev-dependency versions:
  - nose:         1.3 -> 1.3.7
  - coverage:     4.3 -> 5.5
  - nose-timer:   0.6 -> 1.0.1
  - testfixtures: 4.13 -> 6.17.1
  - mock:         1.3 -> 4.0.3

## [0.9.0]

### BREAKING CHANGES

- **CUMULUS-1799**
  - Update cumulus-process-py requirements to CMA 1.2.0
  - Remove python 2 support

## [0.8.0]

- Update package to use CMA-py 1.1.x series.

**Please note that [CMA-python](https://github.com/nasa/cumulus-message-adapter-python) utilizes either [CMA](https://github.com/nasa/cumulus-message-adapter) 1.0.x or 1.1.x series.**

If you wish to continue using the pre 1.1.x series CMA, you will need to explicitly pin it in your project environment if you are pulling the CMA from pypi.

## [0.7.0]

### How to upgrade to 0.7.0
- The cumulus-process-py no longer assumes the structure of input and config given to a processing sublcass. These assumptions have to be added in the `__init__` section of the subclass (see example).
- All methods that have specific assumptions about the structure of the Cumulus message are deprecated. Subclasses should implement these methods in the subclass if they are needed
- Some of the deprecated methods are moved to a new helpers modules can be used by importing them directly from that module

### Added
- Add deprecation warning to the followings methods of the Process class (these methods will be removed in v0.8.0)
- Add example folder with an example implementation of a Process sublcass
- Add localstack to tests

### Changed
- Simplify the structure of Process class to support **CUMULUS-456**
- `clean_all` method now removes the whole temp folder at the end of the process (this solves the problem of lambda functions running out of temporary storage)
- **CUMULUS-456** Use the fileStagingDir to create the URL paths and if none exists, use url_path (this is added to deprecation methods)
- **CUMULUS-477** Updates to use the new bucket structure where each bucket is no longer a string, but an object with name and type (this is added to deprecation methods)

## [0.6.1]

### Changed
- Get cumulus-message-adapter-python from pypi instead of github

## [0.6.0]

### Changed
- Removed the built-in assumptions about the config and input to the Process class when the class is initialized. [CUMULUS-543]
- A new property called `self.regex` is introduced. This property should be set for the `self.gid` property to work properly.

## [0.5.7]
- allow input_keys to be specified in payload
- move existing hardcoded regex to default_keys, used if none in payload
- backwards-compatible, but child classes should rename input_keys to default_keys or they will override inherited logic

## [0.5.6]:
- truncate error strings passed to sfn.send_task_failure()
- log exceptions raised in the handler

## [0.5.5]:
- Peg version of cumulus-message-adapter-python
- Update imports for Python3

## [0.5.4]:
- Fix activity handler for cumulus

## [0.5.3]:
- Fix CLI for processing payloads

## [0.5.2]:

## [0.5.1]:
- Fix passing in of a local path for saving files and output
- Properly clean up downloaded files

## [0.5.0]:
- Multiple bug fixes to work with Cumulus deployment

## [0.4.0b2]:
- Refactored Process class to remove any automatic functionality
- Update to use cumulus-message-adapter
- cumulus-py now public and open source, turned into standard package, docker files removed
- ci updated to auto tag and deploy to PyPi on merge to master

## [0.4.0b1]:
- Refactor Granule class into new Process class
- New payload format

## 0.3.0b2:
- Payloads updated for Cumulus phase 3
- refactored granule class to be more abstracted, payload code moved to aws service module
- added support for multiple output granules
- use regex to determine which input files are which so order does not matter (only that all needed files are supplied, in any order)

[Unreleased]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.7.0...HEAD
[0.7.0]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.6.1...0.7.0
[0.6.1]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.6.0...0.6.1
[0.6.0]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.5.7...0.6.0
[0.5.7]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.5.6...0.5.7
[0.5.6]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.5.5...0.5.6
[0.5.5]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.5.4...0.5.5
[0.5.4]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.5.3...0.5.4
[0.5.3]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.5.2...0.5.3
[0.5.2]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.5.1...0.5.2
[0.5.1]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.5.0...0.5.1
[0.5.0]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.4.0b2...0.5.0
[0.4.0b2]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.4.0b1...0.4.0b2
[0.4.0b1]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.3.0b2...0.4.0b1