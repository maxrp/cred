from cred.Store import Store

import logging
from os import path

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
            "default_recipients":   ['acip', 'bcip'],
            "extension":            '.yaml.gpg',
            "gpg_home":             path.join(fixtures, 'gpghome'),
            "sign":                 True,
            "use_agent":            False,
            "verbose":              True,
        }

        self.creds = Store(**self.config)
        self.creds.passphrase = 'federal-llama-dingus'

    def tearDown(self):
        pass

    def test_arbitrary(self):
        assert self.creds.passphrase == 'federal-llama-dingus'
