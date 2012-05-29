from fabric.api import *
from os import path
import tests

def make_gpg_fixtures(fixtures='./tests/fixtures'):
    """Perform the time & entropy expensive generation of keys for testing."""
    secring = path.join(fixtures, 'secring.gpg')
    if not path.exists(secring):
        tests.util.genkey(fixtures)
    else:
        print 'Skipping key generation, secring exists.'

def clean():
    local('find . -name "*.pyc" -exec rm -rf {} \;')
    local('rm -rf cred.egg-info dist build cred.egg-info pylint.log test.log')

def gpg_clean(fixtures='./tests/fixtures'):
    local('rm -rf {0}/gpghome/*.gpg'.format(fixtures))

def lint():
    local('pylint cred/*.py setup.py tests/*.py | tee pylint.log | less')

def test():
    make_gpg_fixtures()
    local('nosetests -v 2>&1 | tee test.log | less')

def install():
    local('python setup.py install --user')

def reinstall():
    uninstall()
    install()

def uninstall():
    local('pip uninstall cred')
