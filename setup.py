#!/usr/bin/env python
import os
from codecs import open
from setuptools import setup, find_packages

# get dependencies
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')
install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
version_ns = {}
with open(os.path.join(here, "cumulus_process", "version.py"), encoding="utf-8") as f:
    exec(f.read(), version_ns)
__version__ = version_ns["__version__"]

setup(
    name='cumulus_process',
    version=__version__,
    author='Matthew Hanson (matthewhanson), Alireza J (scisco)',
    description='Library for creating Cumulus Process tasks in Python',
    url='https://github.com/nasa-cumulus/cumulus-process-py',
    license='Apache 2.0',
    classifiers=[
        'Programming Language :: Python :: 3.12'
    ],
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    install_requires=install_requires,
)
