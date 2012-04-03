import logging
import os, errno
import sys
import yaml

from cred.Store import Store
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
            config = os.path.expanduser("~") + "/.credconf.yaml"

        with open(config, "r") as config:
            config_keys = yaml.load(config)
 
        self.check_config(config_keys)

        # this causes python-gnupg to emit messages
        config_keys['verbose'] = args.super_verbose

        # ensure the encrypting user is always in the recipient list
        config_keys['default_recipients'].append(config_keys['default_key'])
        # ensure credentials is an absolute path
        config_keys['credentials'] = os.path.abspath(config_keys['credentials'])
        # provide the config keys as the args to creds
        self.creds = Store(**config_keys)

    def add(self, args):
        new_cred = yaml.dump(self.creds.add(args.name), default_flow_style=False)
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
            cred_list = self.creds.list_credentials()
            for namespace in self.creds.list_namespaces():
                sub_creds = [os.path.join(namespace, cred) for cred in self.creds.list_credentials(namespace)]
                cred_list.extend(sub_creds)
            for cred in cred_list:
                # relpath because relpath is how you'll refer to them
                print os.path.relpath(cred, self.creds.credentials)
        return 0

    def check_config(self, config):
        required_keys = [
                            "credentials",
                            "default_key",
                            "default_recipients",
                            "extension",
                            "gpg_home",
                            "sign",
                            "use_agent",
                        ]
        config_keys = config.keys()
        config_keys.sort()
        if config_keys != required_keys:
            missing_set = Set(required_keys) - Set(config_keys)
            excess_set = Set(config_keys) - Set(required_keys)
            for key in missing_set:
                logging.critical("Missing config key: %s", key)
            if excess_set:
                for excess_parameter in excess_set:
                    logging.warn("Excess parameter in config: %s", excess_parameter)
            else:
                raise Exception("Incomplete configuration", "the configuration was missing %d key(s)." % len(missing_set))

    def modify(self, args):
        changed_cred = yaml.dump(self.creds.mod(args.name), default_flow_style=False)
        print "\n\nChanged cred is..."
        print changed_cred
        return 0
