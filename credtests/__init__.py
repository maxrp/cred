"""Basic environment details & attendant functions for the test environment"""

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

# The credtests dir
TESTDIR = os.path.abspath(os.path.dirname(__file__))

# The credtests fixtures subdir
FIXTURESDIR = os.path.join(TESTDIR, 'fixtures')

def gen_keys(fixturesdir=FIXTURESDIR):
    """Generate keys for the test environment fixturesdir."""
    ctx = gpgme.Context()
    os.environ['GNUPGHOME'] = fixturesdir
    result = ctx.genkey(KEYPARAMS)
    key = ctx.get_key(result.fpr, True)
    [uid] = key.uids
    print '{0}\n\t{1}'.format(uid.uid, result.fpr)
    del os.environ['GNUPGHOME']
