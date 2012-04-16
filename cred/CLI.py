import getpass
import glob
import logging
import yaml

from cred.Store import Store, NeedsPassphrase
from os import listdir, path
from sets import Set

class CLI(object):
    def setup(self, args):
        
        # assume we only log critical stuff
        loglevel = logging.CRITICAL

        # upgrade log levels if desired
        if args.verbose:
            loglevel = logging.INFO

        if args.super_verbose:
            loglevel = logging.DEBUG
        
        # set up logging
        logging.basicConfig(
            format='[Cred %(levelname)s] %(asctime)s: %(message)s',
            level=loglevel,
        )

        if not args.config:
            config = path.expanduser("~") + "/.credconf.yaml"

        with open(config, "r") as config:
            self.config = yaml.load(config)
 
        self.__check_config()

        # this causes python-gnupg to emit messages
        self.config['verbose'] = args.super_verbose

        # ensure the encrypting user is always in the recipient list
        self.config['default_recipients'].append(self.config['default_key'])
        # ensure credentials is an absolute path
        self.config['credentials'] = path.abspath(self.config['credentials'])
        # provide the config keys as the args to creds
        self.creds = Store(**self.config)

    def add(self, args):
        cred_path = self.creds.get_path(args.name)

        if path.exists(cred_path):
            raise Exception("Credential exists",
                            "try `cred mod %s`" % args.name)
        
        prompt_defaults = ", ".join(['username', 'password'])

        response = self.__prompt("Add which keys?", prompt_defaults)
        new_keys = response.split(",")

        # aggregate new and modified keys
        new_cred = []
        for key in new_keys:
            key = key.strip()
            new_val = self.__prompt(key)
            new_cred.append("%s: %s" % (key, new_val))

        # dump the yaml from a hopefully successful call to save
        new_cred = yaml.dump(
                             self.creds.save(args.name, new_cred),
                             default_flow_style=False,
                             )
        print "\n\nSaved cred is..."
        print new_cred
        return 0

    def get(self, args):
        if args.name:
            cred = self.__get(args.name)
            if args.fields:
                for field in args.fields:
                    print cred.get(field)
            elif args.list_keys:
                for field in cred:
                    print field
            else:
                print yaml.dump(cred, default_flow_style=False)
        else:
            cred_list = self.list_credentials()
            for namespace in self.list_namespaces():
                for cred in self.list_credentials(namespace):
                    cred_list.append(path.join(namespace, cred))
            for cred in cred_list:
                # relpath because relpath is how you'll refer to them
                print path.relpath(cred, self.config['credentials'])
        return 0
    
    def list_credentials(self, namespace=False):
        pattern = "*" + self.config['extension']
        if namespace:
            creds = path.join(self.config['credentials'], namespace, pattern)
        else:
            creds = path.join(self.config['credentials'], pattern)
        creds = glob.glob(creds)
        return [cred.replace(self.config['extension'], "") for cred in creds]

    def list_namespaces(self):
        namespaces = list()
        for namespace in listdir(self.config['credentials']):
            ns_path = path.join(self.config['credentials'], namespace)
            if path.isdir(ns_path):
                namespaces.append(ns_path)
        return namespaces

    def __check_config(self):
        required_keys = [
                            "credentials",
                            "default_key",
                            "default_recipients",
                            "extension",
                            "gpg_home",
                            "sign",
                            "use_agent",
                        ]
        config_keys = self.config.keys()
        config_keys.sort()
        if config_keys != required_keys:
            missing_set = Set(required_keys) - Set(config_keys)
            excess_set = Set(config_keys) - Set(required_keys)
            for key in missing_set:
                logging.critical("Missing config key: %s", key)
            if excess_set:
                for excess_parameter in excess_set:
                    del self.config[excess_parameter]
                    logging.warn(
                                    "Excess parameter in config: %s",
                                    excess_parameter
                                    )
            else:
                raise Exception(
                                "Incomplete configuration",
                                "missing %d key(s)." % len(missing_set)
                                )
    
    def __prompt(self, query, default=False):
        if default:
            prompt = "%s [%s]:  " % (query, default)
        else:
            prompt = "%s: " % query
        logging.debug("Asking for %s", query)
        response = raw_input(prompt)
        if not response:
            return default
        else:
            return response

    def __get(self, name):
        try:
            return self.creds.get(name)
        except NeedsPassphrase as err:
            self.creds.passphrase = getpass.getpass()
            return self.__get(name)

    def modify(self, args):
        orig_cred = self.__get(args.name)
        orig_cred_keys = orig_cred.keys()
        prompt_defaults = ", ".join(orig_cred_keys)

        response = self.__prompt("Modify", prompt_defaults)
        mod_keys = [key.strip() for key in response.split(",")]

        # aggregate new and modified keys
        new_cred = []
        for key in mod_keys:
            value = orig_cred.get(key, False)
            new_val = self.__prompt(key, value)
            new_cred.append("%s: %s" % (key, new_val))

        # copy unchanged keys from the orig_cred
        for key in orig_cred_keys:
            if key not in mod_keys:
                new_cred.append("%s: %s" % (key, orig_cred[key]))

        changed_cred = yaml.dump(
                                 self.creds.save(args.name, new_cred),
                                 default_flow_style=False,
                                )
        print "\n\nChanged cred is..."
        print changed_cred
        return 0
