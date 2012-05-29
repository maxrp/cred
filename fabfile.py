from fabric.api import *
import gpgme
import os
import credtests

def make_fixtures(fixtures=credtests.FIXTURESDIR):
    """Perform the time & entropy expensive generation of keys for testing."""
    secring = os.path.join(fixtures, 'secring.gpg')
    if not os.path.exists(secring):
        credtests.gen_keys(fixtures)
    else:
        print 'Skipping key generation, secring exists:'
        list_test_keys()

def clean():
    local('find . -name "*.pyc" -exec rm -rf {} \;')
    local('rm -rf cred.egg-info dist build cred.egg-info pylint.log test.log')

def clean_fixtures(fixtures=credtests.FIXTURESDIR):
    """Delete any generated testing resources."""
    test_files = os.path.join(fixtures, '*.gpg*')
    local('rm -rf {0}'.format(test_files))

def lint():
    local('pylint cred/*.py setup.py tests/*.py | tee pylint.log | less')

def list_test_keys(fixtures=credtests.FIXTURESDIR):
    os.environ['GNUPGHOME']=fixtures
    ctx = gpgme.Context()
    secring = os.path.join(fixtures, 'secring.gpg')
    with open(secring, 'rb') as keyring:
        keys = ctx.import_(keyring)
        [(fingerprint, _, _)] = keys.imports
        for key in ctx.keylist():
            for uid in key.uids:
                print "{0.uid}\n\t{1}".format(uid, fingerprint)
        del os.environ['GNUPGHOME']

def test():
    make_fixtures()
    local('nosetests -v 2>&1 | tee test.log | less')

def install():
    local('python setup.py install --user')

def reinstall():
    uninstall()
    install()

def uninstall():
    local('pip uninstall cred')
