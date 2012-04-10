import getpass
import gnupg
import logging
import os, errno
import yaml

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
            self.passphrase = getpass.getpass()

        self.gpg = gnupg.GPG(
                                gnupghome=self.gpg_home,
                                use_agent=self.use_agent,
                                verbose=self.verbose
                            )

    def __open(self, path, mode):
        try:
            logging.info("Opening: %s, %s", path, mode)
            stream = open(path, mode)
        except IOError as err:
            raise Exception(err.strerror, err.filename)
        else:
            return stream
    
    def __ensure_path(self, path):
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
            logging.debug("Creating the nonexistant %s.", path)
        

    def __cryptwrap(self, fun, cred, *args, **kwargs):
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
        # clone the method from the gpg class
        logging.debug("Trying method: %s on: %s", fun, cred)
        method = getattr(self.gpg, fun)
        if not self.use_agent:
            kwargs['passphrase'] = self.passphrase 

        cred = method(cred, *args, **kwargs)

        if cred.ok:
            return cred
        else:
            raise Exception("%s failed" % fun, cred.status)
            
    def __decrypt(self, cred, *args, **kwargs):
        # TODO: implement signature verification
        return self.__cryptwrap('decrypt_file', cred, *args, **kwargs)

    def __encrypt(self, cred, *args, **kwargs):
        if self.sign:
            kwargs['sign'] = self.default_key
        return self.__cryptwrap('encrypt', cred, *args, **kwargs)

    def mod(self, cred):
        orig_cred = self.get(cred)
        orig_cred_keys = orig_cred.keys()
        prompt_defaults = ", ".join(orig_cred_keys)

        response = self.__prompt("Modify", prompt_defaults)
        mod_keys = response.split(",")

        # aggregate new and modified keys
        new_cred = []
        for key in mod_keys:
            key = key.strip()
            value = orig_cred.get(key, False)
            new_val = self.__prompt(key, value)
            new_cred.append("%s: %s" % (key, new_val))

        # copy unchanged keys from the orig_cred
        for key in orig_cred_keys:
            if key not in mod_keys:
                new_cred.append("%s: %s" % (key, orig_cred[key]))
        
        return self.save(cred, new_cred)


    def save(self, cred, new_cred):
        path = self.get_path(cred)
        with self.__open(path, "wb") as new_cred_file:
            logging.debug("Saving cred: %s" , path)
            new_cred = "\n".join(new_cred)
            encrypted_cred = self.__encrypt(new_cred, self.default_recipients)
            new_cred_file.write(str(encrypted_cred))
            new_cred_file.flush()

        return self.get(cred)

    def get_path(self, cred):
        path = os.path.join(self.credentials, cred + self.extension)
        # strip any file names from the path
        parent_path = os.path.dirname(path)
        self.__ensure_path(parent_path)
        return path
    
    def get(self, cred):
        path = self.get_path(cred)
        with self.__open(path, "rb") as encrypted_file:
            decrypted = self.__decrypt(encrypted_file)

        try:
            data = yaml.load(str(decrypted))
        except yaml.YAMLError as err:
            # surpress most of YAMLError to avoid randomly sending to stderr
            raise Exception(err.context, err.problem)
        else:
            return data

