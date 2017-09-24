#!/usr/bin/env python

import os
import re
import sys

from codecs import open

from setuptools import setup
from setuptools.command.test import test as TestCommand


packages = [
    'r4',
    'r4.client',
    'r4.intermediate',
]

requires = []
version = '0.0.1'

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='r4',
    version=version,
    description='Automatically distributed S3-like file storage service',
    long_description=readme,
    author='William Baskin, Robert Wagner',
    url='http://github.com/buckbaskin/r4',
    packages=packages,
    package_dir={'r4': 'r4'},
    include_package_data=True,
    install_requires=requires,
    license='MIT',
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ),
)

