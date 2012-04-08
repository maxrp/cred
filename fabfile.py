from fabric.api import local

def install():
    local('python setup.py install --user')

def reinstall():
    uninstall()
    install()

def uninstall():
    local('pip uninstall cred')
