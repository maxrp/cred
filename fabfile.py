from fabric.api import local

def lint():
    local('pylint cred/*.py setup.py | tee pylint.log | less')

def install():
    local('python setup.py install --user')

def reinstall():
    uninstall()
    install()

def uninstall():
    local('pip uninstall cred')
