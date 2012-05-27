import gpgme

KEYPARAMS = """
<GnupgKeyParms format="internal">
%echo Generating a testing fixture key (this could take a minute)...
Key-Type: DSA
Key-Length: 1024
subkey-Type: ELG-E
Subkey-Length: 1024
Name-Real: Sir. Dr. Fakee McFakerton XIV Esq. Jr.
Name-Comment: King of Fakareas
Name-Email: fakef@example.com
Expire-Date: 0
%homedir {gpghome}
%pubring pubring.pub
%secring secring.sec
%commit
%echo Key generation complete!
</GnupgKeyParms>
"""

def genkeys(): 
    ctx = gpgme.Context()
    params = KEYPARAMS.format(gpghome='/home/maxp/code/cred/tests/fixtures/gpghome')
    result = ctx.genkey(params)
    print result.fpr

genkeys()
