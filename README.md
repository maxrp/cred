cred: an easy password repository for account identity management
=========================================================

cred is a tool to enable easy manipulation of a directory tree populated 
with GnuPG encrypted YAML.

Examples
--------
- Get data from stores
  - Retrieve key value pairs from a named store
            
            $ cred get example.com username password
            username: foobar
            password: quuxxyzzy

  - Retrieve the entire set of data from a store
            
            $ cred get example.com
            username: foobar
            password: quuxxyzzy
            uri: https://example.com/login

  - List attributes in a store
             
             $ cred get --keys example.com
             uri
             username
             password

- Create new stores
        
        $ cred add example.com
        Password:
        Add which keys?: username, password
        username: foobar
        password: quuxxyzzy
        
        Saved cred is...
        password: quuxxyzzy
        username: foobar

- Modify existing credentials for a domain
- Using directories to namespace credentials under the configured credential path
- Listing credentials
- gpg-agent support

Requirements
------------
- [python-gnupg][1]
- [PyYAML][2]
- [GnuPG][3]
  - A GPG key and some good sense
- Python 2.7

You might also want...
-----------
- Credentials for some stuff you want to encrypt with your gpg public key and possibly the public keys of some associates.
- [gnupg.vim][4] A nice vim plugin for creating and modifying gpg encrypted text files.

Setup
-----
1. Ensure you have the materials listed above 
1. Copy the example config to it's proper name:
        
        cp ./examples/credconf.yaml ~/.credconf.yaml 
2. Edit ~/.credconf.yaml. Namely:
    - Set "gpg\_home" to the right value
    - Set "credentials" to the place you would like to store these credentials. If the directory does not exist, it will be created.
    - Set "default\_key" to the UID of key you want to sign with, i.e. "Bob" or "Bob Dobbs" or "Bob Dobbs \<bob@dobbs.com\>"
    - Add UIDs of trusted keys to defaul\_recipients, if you like (the default\_key will be appended to this list automatically)
3. Install the script:
        
        python setup.py install --user
4. Make sure you have ~/.local/bin (or whatever you use) in your path.
4. Try it out!
        
        cred --help
        cred add example.net
        cred get --keys example.net
        cred get example.net password
        cred add alter-ego/example.net
        cred modify alter-ego/example.net
        cred get
6. `cat lib/bash_completion.sh >> .bashrc` or whatever; for local completions I have a ~/.bash\_completions which is sourced in my .bashrc and it's not an awful way to deal with personal completion preferences.

Tips
----
The quickest way to get a workable gpg-agent environment for any scenario:
        
        gpg-agent --pinentry-program /usr/bin/pinentry-curses --daemon /bin/bash

[1]: http://pypi.python.org/pypi/python-gnupg   "python-gnupg"
[2]: http://pypi.python.org/pypi/PyYAML         "PyYAML"
[3]: http://www.gnupg.org/                      "GnuPG"
[4]: http://www.vim.org/scripts/script.php?script_id=3645   "gnupg.vim"
