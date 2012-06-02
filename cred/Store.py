import gpgme
import logging
import os, errno
import yaml

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

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
        ):
        # force a sane default umask
        os.umask(0077)
        self.credentials = credentials
        self.default_key = default_key
        self.extension = extension
        self.passphrase = None
        self.sign = sign

        # does the passwords, dir exist? do we have perms?
        self.__ensure_path(self.credentials)

        # check to see if there's actually an agent in the env
        agent = os.environ.get("GPG_AGENT_INFO", False)

        # wanting to use an agent is cool, but if you don't have one...
        if not agent or not use_agent:
            use_agent = False

        # initialize the gpgme context
        self.gpg = gpgme.Context()
        self.gpg.armor = True

        # load the keys of the default recipients
        self.default_recipients = list()
        for keyid in default_recipients:
            self.default_recipients.append(self.gpg.get_key(keyid))
        # load self
        self.default_key = self.gpg.get_key(default_key)
        self.default_recipients.append(self.default_key)

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
            
    def __decrypt(self, name):
        """Internal decrypt function."""
        # TODO: implement signature verification
        path = self.get_path(name)
        with self.__open(path, "rb") as encrypted_file:
            # is there a better way for: file -> buffer ?
            ciphertext = BytesIO()
            for line in encrypted_file.readlines():
                ciphertext.write(line)
        
        # rewind the cipher and decrypt to the cred buffer
        ciphertext.seek(0)
        cred = BytesIO()
        self.gpg.decrypt(ciphertext, cred)
        
        # rewind cred and return all of it
        cred.seek(0)
        return cred.read()

    def __encrypt(self, name, data):
        """Internal encrypt function."""
        # TODO: implement signing
        plaintext = BytesIO(data)
        ciphertext = BytesIO()
        try:
            self.gpg.encrypt(self.default_recipients,
                             gpgme.ENCRYPT_ALWAYS_TRUST,
                             plaintext,
                             ciphertext)
        except:
            raise

        path = self.get_path(name)
        # rewind ciphertext
        ciphertext.seek(0)
        with self.__open(path, "wb") as encrypted_file:
            for line in ciphertext.readlines():
                encrypted_file.write(line.encode('ASCII'))
            encrypted_file.flush()

    def save(self, name, new_cred):
        """Take a credential name and a YAML doc, encrypt it per the config and
        write it to disk, flushing immediately. The cred is represented as it 
        would be loaded."""
        logging.debug("Saving cred: %s" , name)
        new_cred = "\n".join(new_cred)
        self.__encrypt(name, new_cred)
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
