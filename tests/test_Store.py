from cred.Store import Store

import logging
import shutil
from os import path, rmdir

class TestStore(object):

    def setUp(self):
        
        # The code logs, so lets save those
        log_file = path.join(path.dirname(__file__), 'logs/TestStore.log')
        log_format = '[TestStore %(levelname)s] %(asctime)s: %(message)s'
        logging.basicConfig(
                            format=log_format,
                            level=logging.DEBUG,
                            filename=log_file
                            )
        
        # Where fixture resource files are kept
        fixtures = path.join(path.dirname(__file__), 'fixtures')

        # test config for Store
        self.config = {
            "credentials":          path.join(fixtures, 'credentials'),
            "default_key":         'fakekey',
            "default_recipients":   [],
            "extension":            '.yaml.gpg',
            "gpg_home":             path.join(fixtures, 'gpghome'),
            "sign":                 True,
            "use_agent":            False,
            "verbose":              True,
        }

        self.creds = Store(**self.config)
        self.creds.passphrase = 'federal-llama-dingus'

    def tearDown(self):
        # remove the autocreated credential directory
        shutil.rmtree(self.config['credentials'])

    def test_a(self):
        """Does instantiation of the Store object create a credentials
           directory?"""
        assert path.exists(self.config['credentials'])
