Cred: a tool for querying GPG encrypted YAML format credentials
===============================================================

It doesn't really do much useful yet.

Requirements
------------
- [python-gnupg][1]
- [PyYAML][2]
- [GnuPG][3]
  - A GPG private key and some good sense
- Python 2.7

Setup
-----
1. Copy the example config to it's proper name:
        
        cp conf.example.yaml conf.yaml 
2. Edit conf.yaml to your liking
3. Wish this tool had an option to populate an encrypted file addressed to your configured recipients with it's schema dumper
4. Figure out how to use [gnupg.vim][4] instead until I get around to writing the afformentioned component

[1]: http://pypi.python.org/pypi/python-gnupg   "python-gnupg"
[2]: http://pypi.python.org/pypi/PyYAML         "PyYAML"
[3]: http://www.gnupg.org/                      "GnuPG"
[4]: http://www.vim.org/scripts/script.php?script_id=3645   "gnupg.vim"
