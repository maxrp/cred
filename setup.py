#!/usr/bin/python

from distutils.core import setup

setup(name='cred',
    version='0.9',
    description='GnuPG frontend for storing credentials in YAML',
    author='Max R.D. Parmer',
    author_email='m@x-pl.us',
    scripts=['bin/cred'],
)
