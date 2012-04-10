cred: an encrypted repository for account management
====================================================

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
        Add which keys? [username, password]:
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
- recent Python, [python-gnupg][1] and [PyYAML][2]
- [GnuPG][3] (and a keypair)

You also might like...
-----------
- Some 'key: value' type stuff (like login information) you want to encrypt with keys on your GPG keyring
- [gnupg.vim][4] A nice vim plugin for creating and modifying gpg encrypted text files.

Setup
-----
- [Know where you're at with your terminal scrollback][5]
1. Clone the repository:
        
        git clone https://github.com/maxrp/cred.git && cd cred
2. Install the script:
        
        python setup.py install --user
1. Copy the example config to it's proper place:
        
        cp ./examples/credconf.yaml ~/.credconf.yaml 
2. Edit ~/.credconf.yaml. Namely:
    - Set "gpg\_home" to the right value
    - Set "credentials" to the place you would like to store these credentials. If the directory does not exist, it will be created.
    - Set "default\_key" to the UID of key you want to sign with, i.e. "Bob" or "Bob Dobbs" or "Bob Dobbs \<bob@dobbs.com\>"
    - Add UIDs of trusted keys to default\_recipients, if you like (the default\_key will be appended to this list automatically)
4. Make sure you have ~/.local/bin in your path.
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
[5]: http://www.securityfocus.com/archive/1/521920/30/0/threaded
