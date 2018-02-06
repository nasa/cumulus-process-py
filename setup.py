#!/usr/bin/env python
import os
from codecs import open
from setuptools import setup, find_packages
import imp

__version__ = imp.load_source('cumulus_process.version', 'cumulus_process/version.py').__version__

# get dependencies
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')
install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
#with open(os.path.join(here, 'requirements-dev.txt'), encoding='utf-8') as f:
#    all_reqs = f.read().split('\n')
#tests_require = [x.strip() for x in all_reqs if 'git+' not in x]


setup(
    name='cumulus_process',
    version=__version__,
    author='Matthew Hanson (matthewhanson), Alireza J (scisco)',
    description='Library for creating Cumulus Process tasks in Python',
    url='https://github.com/nasa-cumulus/cumulus-process-py',
    license='Apache 2.0',
    classifiers=[
        'Topic :: Software Development :: Libraries',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    install_requires=install_requires,
    #tests_require=tests_require,
)
