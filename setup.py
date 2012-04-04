#!/usr/bin/python

import os
from setuptools import setup, find_packages

kwds = {}

# Read the long description from the README.md
thisdir = os.path.abspath(os.path.dirname(__file__))
f = open(os.path.join(thisdir, 'README.md'))
kwds['long_description'] = f.read()
f.close()

setup(name='cred',
    version='0.9.0.3',
    description='GnuPG frontend for storing credentials in YAML',
    install_requires=[
        'python-gnupg>=0.2.9',
        'PyYAML>=3.10',
    ],
    author='Max R.D. Parmer',
    license="GPL",
    author_email='m@x-pl.us',
    entry_points={
        'console_scripts': [
            'cred = cred.Main:main',
        ],
    },
    packages=find_packages(),
    **kwds
)
