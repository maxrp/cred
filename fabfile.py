from fabric.api import local
from os import path

def make_gpg_fixtures(fixtures='./tests/fixtures'):
    """Perform the time & entropy expensive generation of keys for testing."""
    secring_exists = path.exists('{}/gpghome/secring.gpg'.format(fixtures))
    pubring_exists = path.exists('{}/gpghome/pubring.gpg'.format(fixtures))
    if not secring_exists and not pubring_exists:
        local('gpg --homedir={0} --batch \
              --gen-key {0}/gpg-gen-key.params'.format(fixtures))
    else:
        print 'Skipping key generation, keyrings exist.'

def clean():
    local('find . -name "*.pyc" -exec rm -rf {} \;')
    local('rm -rf cred.egg-info dist build cred.egg-info pylint.log test.log')

def gpg_clean(fixtures='./tests/fixtures'):
    local('rm -rf {0}/gpghome/*'.format(fixtures))

def lint():
    local('pylint cred/*.py setup.py tests/*.py | tee pylint.log | less')

def test():
    make_gpg_fixtures()
    local('nosetests -v | tee test.log | less')

def install():
    local('python setup.py install --user')

def reinstall():
    uninstall()
    install()

def uninstall():
    local('pip uninstall cred')
