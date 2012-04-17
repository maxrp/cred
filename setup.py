#!/usr/bin/python

import os
from setuptools import setup, find_packages


def get_desc():
    """Read the long description from the README.md"""
    pwd = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(pwd, 'README.md')) as readme:
        return readme.read()

setup(name='cred',
    version='0.9.0.5',
    description='GnuPG frontend for storing credentials in YAML',
    install_requires=[
        'argparse>=1.1',
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
    long_description=get_desc(),
)
