import glob
import logging
import os
import yaml

from cred.Store import Store
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
        new_cred = yaml.dump(
                                self.creds.add(args.name),
                                default_flow_style=False
                                )
        print "\n\nSaved cred is..."
        print new_cred
        return 0

    def get(self, args):
        if args.name:
            cred = self.creds.get(args.name)
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

    def modify(self, args):
        changed_cred = yaml.dump(
                                    self.creds.mod(args.name),
                                    default_flow_style=False
                                    )
        print "\n\nChanged cred is..."
        print changed_cred
        return 0
