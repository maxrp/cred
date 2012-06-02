"Test the core storage wrapper around yaml and gpg: cred.Store"""

import logging
import shutil
from os import path

import credtests
from cred.Store import Store

class TestStore(object):
    """Environment details for testing cred.Store"""

    def setUp(self):
        """Initialize the environment: logging, fake config"""
        
        # The code logs, so lets save those
        log_file = path.join(path.dirname(__file__), 'logs/TestStore.log')
        log_format = '[TestStore %(levelname)s] %(asctime)s: %(message)s'
        logging.basicConfig(
                            format=log_format,
                            level=logging.DEBUG,
                            filename=log_file
                            )
        
        # test config for Store
        self.config = {
            "credentials":          path.join(credtests.FIXTURESDIR, 
                                              'credentials'),
            "default_key":         'fakef@example.com',
            "default_recipients":   ['fakef@example.com'],
            "extension":            '.yaml.gpg',
            "gpg_home":             credtests.FIXTURESDIR,
            "sign":                 True,
            "use_agent":            False,
            "verbose":              True,
        }

        self.creds = Store(**self.config)
        
        self.test_cred = {'username': 'wat', 'password': 'hummus'}
        self.test_name = 'example.com'

        # what raw_input data looks like
        self.test_cred_ui = list()
        for key, value in self.test_cred.iteritems():
            self.test_cred_ui.append("{0}: {1}\n".format(key, value))

    def tearDown(self):
        """Remove the autocreated credential directory and contents"""
        shutil.rmtree(self.config['credentials'])

    def test_a(self):
        """Does instantiation of the Store object create a credentials dir?"""
        assert path.exists(self.config['credentials'])

    def test_b(self):
        """Does Store.save() work?"""
        saved = self.creds.save(self.test_name, self.test_cred_ui)
        assert saved == self.test_cred

    def test_c(self):
        """Does Store.get() work?"""
        saved = self.creds.save(self.test_name, self.test_cred_ui)
        stored = self.creds.get(self.test_name)
        # the return from get() should be the same as the return from save()
        assert stored == saved
        # and the return from get() should be the same as the test_cred dict
        assert stored == self.test_cred

    def test_d(self):
        """Does Store.{save,get}('ns/{test_name}') work?"""
        fake_ns = 'ns'
        namespace = "{0}/{1.test_name}".format(fake_ns, self)
        saved = self.creds.save(namespace, self.test_cred_ui)
        assert saved == self.test_cred
        # the directory which should be autocreated
        expected_ns_path = path.join(self.config['credentials'], fake_ns)
        assert path.exists(expected_ns_path)

    def test_e(self):
        """Are file creations constrained to the configured directory?"""
        bogus_ns = '../../BOGUS-ACCIDENT'
        namespace = "{0}/{1.test_name}".format(bogus_ns, self)
        try:
            self.creds.save(namespace, self.test_cred_ui)
        except Exception as err:
            # Store could raise better exceptions, but does it raise the one
            # it should raise?
            msg, explanation = err.args
            logging.debug("%s: %s", msg, explanation)
            assert msg == 'Path error'
        else:
            # no matter what else happened, check that the dir wasn't made
            attempted_path = path.join(self.config['credentials'], bogus_ns)
            assert not path.exists(attempted_path)
