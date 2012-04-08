from fabric.api import local

def clean():
    local('find . -name "*.pyc" -exec rm -rf {} \;')
    local('rm -rf cred.egg-info dist build cred.egg-info pylint.log')

def lint():
    local('pylint cred/*.py setup.py | tee pylint.log | less')

def install():
    local('python setup.py install --user')

def reinstall():
    uninstall()
    install()

def uninstall():
    local('pip uninstall cred')
