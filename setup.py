#!/usr/bin/python

import os
from distutils.core import setup

kwds = {}

# Read the long description from the README.txt
thisdir = os.path.abspath(os.path.dirname(__file__))
f = open(os.path.join(thisdir, 'README.md'))
kwds['long_description'] = f.read()
f.close()

setup(name='cred',
    version='0.9',
    description='GnuPG frontend for storing credentials in YAML',
    author='Max R.D. Parmer',
    license="GPL",
    author_email='m@x-pl.us',
    scripts=['bin/cred'],
    **kwds
)
