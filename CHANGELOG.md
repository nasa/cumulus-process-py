# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/cumulus-nasa/cumulus-process-py/compare/0.5.7...HEAD
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