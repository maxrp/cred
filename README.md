Cred: a tool for querying GPG encrypted YAML format credentials
===============================================================

A tool for storing passwords in a regular and readily manipulable encrypted format.

Right now it's pretty good at:

- Retrieving the credentials for a domain
  - all at once or by attribute
  - listing attributes
- Writing new credentials for a domain
- Using gpg-agent

Requirements
------------
- [python-gnupg][1]
- [PyYAML][2]
- [GnuPG][3]
  - A GPG private key and some good sense
- [gnupg.vim][4] (pretty much vital for anyone dealing with gpg encrypted text files)
- Python 2.7
- Credentials for some stuff you want to encrypt with your gpg private key to a list of N recipients
  - I'm pretty sure this tool could be coerced to work with GnuPG in symmetric mode, but I haven't tried

Setup
-----
1. Ensure you have the materials listed above 
1. Copy the example config to it's proper name:
        
        cp example.credconf.yaml ~/.credconf.yaml 
2. Edit .credconf.yaml to your liking (Tip: make sure default\_recipients is a list including at least "your name")
4. try it out!
        
        ./cred --help
        ./cred --save example.net
        ./cred example.net

Tips
----
The quickest way to get a workable gpg-agent environment for any scenario:
        
        gpg-agent --pinentry-program /usr/bin/pinentry-curses --daemon /bin/bash

[1]: http://pypi.python.org/pypi/python-gnupg   "python-gnupg"
[2]: http://pypi.python.org/pypi/PyYAML         "PyYAML"
[3]: http://www.gnupg.org/                      "GnuPG"
[4]: http://www.vim.org/scripts/script.php?script_id=3645   "gnupg.vim"
