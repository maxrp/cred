import getpass
import gnupg
import logging
import os, errno
import yaml

class NeedsPassphrase(Exception):
    pass

class Store(object):
    def __init__(
            self,
            credentials,
            default_key,
            default_recipients,
            extension,
            gpg_home,
            sign,
            use_agent,
            verbose,
        ):
        # force a sane default umask
        os.umask(0077)

        self.credentials = credentials
        self.default_key = default_key
        self.default_recipients = default_recipients
        self.extension = extension
        self.gpg_home = gpg_home
        self.passphrase = None
        self.sign = sign
        self.use_agent = use_agent
        self.verbose = verbose

        # checking the veracity of the config
        # does the passwords, dir exist? do we have perms?
        self.__ensure_path(self.credentials)

        # check to see if there's actually an agent in the env
        self.agent = os.environ.get("GPG_AGENT_INFO", False)

        # wanting to use an agent is cool, but if you don't have one...
        if not self.agent or not self.use_agent:
            # whether this is the setting or the fallback, False henceforth
            self.use_agent = False
            logging.debug("Prompting for password.")
            #self.passphrase = getpass.getpass()

        self.gpg = gnupg.GPG(
                                gnupghome=self.gpg_home,
                                use_agent=self.use_agent,
                                verbose=self.verbose
                            )

    def __open(self, path, mode):
        """Wrap open() for logging, error clarification (probably should move 
        to the CLI class)."""
        try:
            logging.info("Opening: %s, %s", path, mode)
            stream = open(path, mode)
        except IOError as err:
            raise Exception(err.strerror, err.filename)
        else:
            return stream
    
    def __ensure_path(self, path):
        """Provided the requested credential path is within the right subpath,
        create it or re-raise the error (if the error isn't that it exists."""
        requested_path = os.path.abspath(path)
        prefix = os.path.commonprefix([requested_path, self.credentials])
        # constrain to subpaths of the configured credential directory
        if prefix != self.credentials:
            message = '''the requested path: \n\t %s\nis outside the configured
            credential directory:\n\t%s''' % (requested_path, self.credentials)
            raise Exception('Path error', message)
        try:
            os.makedirs(path)
        except OSError as err:
            if err.errno != errno.EEXIST:
                raise
        else:
            logging.debug("Created the nonexistant %s.", path)
        

    def __cryptwrap(self, fun, encrypted_file, *args, **kwargs):
        """
        A helper function to enforce some basic logic (mostly injecting a
        passphrase if necessary) and implement logging of calls out to the 
        gnupg library.

        I should eventually handle some of the recoverable cases. Potential 
        values of cred.status are:
            'signature bad'
            'signature good'
            'signature valid'
            'signature error'
            'no public key'
            'need symmetric passphrase'
            'decryption incomplete'
            'encryption incomplete'
            'decryption ok'
            'encryption ok'
            'invalid recipient'
            'key expired'
            'sig created'
            'sig expired'
            'need passphrase'
        """
        logging.debug("Trying method: %s", fun)
        
        # clone the method from the gpg class
        method = getattr(self.gpg, fun)
        
        if self.passphrase:
            kwargs['passphrase'] = self.passphrase 

        cred = method(encrypted_file, *args, **kwargs)

        if cred.ok:
            return cred
        elif cred.status == 'need passphrase':
            raise NeedsPassphrase()
        else:
            raise Exception("%s failed" % fun, cred.status)
            
    def __decrypt(self, name, *args, **kwargs):
        """Internal decrypt function."""
        # TODO: implement signature verification
        path = self.get_path(name)
        with self.__open(path, "rb") as encrypted_file:
            return self.__cryptwrap('decrypt_file', encrypted_file, *args, **kwargs)

    def __encrypt(self, name, data, *args, **kwargs):
        """Internal encrypt function."""
        if self.sign:
            kwargs['sign'] = self.default_key
        path = self.get_path(name)
        with self.__open(path, "wb") as encrypted_file:
            encrypted_cred = self.__cryptwrap('encrypt', data, *args, **kwargs)
            encrypted_file.write(str(encrypted_cred))
            encrypted_file.flush()

    def save(self, name, new_cred):
        """Take a credential name and a YAML doc, encrypt it per the config and
        write it to disk, flushing immediately. The cred is represented as it 
        would be loaded."""
        logging.debug("Saving cred: %s" , name)
        new_cred = "\n".join(new_cred)
        self.__encrypt(name, new_cred, self.default_recipients)
        return self.get(name)

    def get_path(self, name):
        """Resolve a name like example.com or alter-ego/example.com to a path 
        as per the configuration."""
        path = os.path.join(self.credentials, name + self.extension)
        # strip any file names from the path
        parent_path = os.path.dirname(path)
        self.__ensure_path(parent_path)
        return path
    
    def get(self, name):
        """Load a credential by name, decrypting in the process."""
        decrypted = self.__decrypt(name)

        try:
            data = yaml.load(str(decrypted))
        except yaml.YAMLError as err:
            # surpress most of YAMLError to avoid randomly sending to stderr
            raise Exception(err.context, err.problem)
        else:
            return data

