"""Utilities for test cases."""

import gpgme
import os

KEYPARAMS = """
<GnupgKeyParms format="internal">
    Key-Type: DSA
    Key-Length: 1024
    subkey-Type: ELG-E
    Subkey-Length: 1024
    Name-Real: Sir. Dr. Fakee McFakerton XIV Esq. Jr.
    Name-Comment: King of Fakareas
    Name-Email: fakef@example.com
    Expire-Date: 0
</GnupgKeyParms>
"""

def genkeys(fixturesdir):
    """Generate keys for the test environment fixturesdir."""
    ctx = gpgme.Context()
    os.environ['GNUPGHOME'] = fixturesdir
    result = ctx.genkey(KEYPARAMS)
    key = ctx.get_key(result.fpr, True)
    [uid] = key.uids
    print '{0}\n\t{1}'.format(uid.uid, result.fpr)
    del os.environ['GNUPGHOME']

if __name__ == '__main__':
    print 'Generating a key with the parameters:\n{}'.format(KEYPARAMS)
    testdir = os.path.dirname(__file__)
    fixturesdir = os.path.join(testdir, 'fixtures')
    genkeys(fixturesdir)
