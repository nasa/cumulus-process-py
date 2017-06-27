#!/usr/bin/env python
import os
from codecs import open
from setuptools import setup, find_packages
import imp

here = os.path.abspath(os.path.dirname(__file__))
__version__ = imp.load_source('cumulus_dataname.version', 'cumulus_dataname/version.py').__version__

# get the dependencies and installs
# python-setuptools cannot process 'git+' style dependencies. Install with
# `pip -r requirements.txt` before running setup on this package
with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    reqs = f.read().split('\n')
install_requires = [x.strip() for x in reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in reqs if 'git+' in x]
with open(os.path.join(here, 'requirements-dev.txt'), encoding='utf-8') as f:
    dev_reqs = f.read().split('\n')
tests_require = [x.strip() for x in dev_reqs if 'git+' not in x]


setup(
    name='cumulus_datanae',
    version=__version__,
    author='authorname',
    description='Library for processing DATANAME',
    url='https://github.com/nasa-cumulus/docker-DATANAME',
    license='Apache 2.0',
    classifiers=[
        'Framework :: Pytest',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: Freeware',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': ['cumulus-DATANAME=cumulus_dataname.main:cli']
    },
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links,
    tests_require=tests_require
)
