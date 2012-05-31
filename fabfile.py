from fabric.api import *
import gpgme
import os
import credtests

def _make_fixtures(fixtures=credtests.FIXTURESDIR):
    """Perform the time & entropy expensive generation of keys for testing."""
    secring = os.path.join(fixtures, 'secring.gpg')
    if not os.path.exists(secring):
        credtests.gen_keys(fixtures)
    else:
        print 'Skipping key generation, secring exists.'

def clean():
    """Removes pyc, egg-info, dist, build and so on."""
    local('find . -name "*.pyc" -exec rm -rf {} \;')
    local('rm -rf cred.egg-info dist build cred.egg-info *.log')

def lint():
    """Run pylint on the package and tests."""
    local('pylint cred/*.py setup.py credtests/*.py | tee pylint.log | less')

def list_test_keys(fixtures=credtests.FIXTURESDIR):
    """List keys available for the test process."""
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
    """Run and log nosetests, generating test GPG keys if needed."""
    _make_fixtures()
    list_test_keys()
    local('nosetests -v 2>&1 | tee test.log | less')

def install():
    local('python setup.py install --user')

def reinstall():
    uninstall()
    install()

def uninstall():
    local('pip uninstall cred')
