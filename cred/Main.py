#!/usr/bin/env python

__author__ = "Max Parmer <maxp@pdx.edu>"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__maintainer__ = "Max Parmer"
__email__ = "maxp@pdx.edu"
__status__ = "Development"

import argparse
import logging
import sys

from cred.CLI import CLI

class CredsArgParser(argparse.ArgumentParser):
    def error(self, message):
        logging.critical(message)
        self.print_help()
        sys.exit(2)

class Main(CLI):
    def __init__(self):
        description = "Query passwords from GPG encrypted files."
        parser = CredsArgParser(description=description)

        parser.add_argument('-c', '--config', dest='config', default=False,
            help="An alternate configuration path. Default: ~/.credconf.yaml")
        parser.add_argument('-v', '--verbose', dest='verbose',
            action='store_true', default=False, help="Informational messages.")
        parser.add_argument('-vv', '--super-verbose', dest='super_verbose',
            action='store_true', default=False, help="Debug messages.")

        subparsers = parser.add_subparsers(help='Verbs for cred manipulation.')

        add_parser = subparsers.add_parser('add',
            help='Add a credential or add a key to a credential.')
        add_parser.add_argument('name', nargs="?",
            help="The name of the credential to add, i.e. example.com")
        add_parser.set_defaults(func=self.add)

        get_parser = subparsers.add_parser('get',
            help='Get credential contents or credential keys.')
        get_parser.add_argument('-k', '--keys', dest='list_keys',
            action='store_true', help='List only the keys in a credential.')
        get_parser.add_argument('name', nargs="?", default=False,
            help="""The name of the credential to get contents of. If no name is 
            specified, lists all credentials.""")
        get_parser.add_argument('fields', default=False, nargs="*",
            help="""The name of the field or fields to get. If no fields are 
            specified, all fields are returned.""")
        get_parser.set_defaults(func=self.get)

        mod_parser = subparsers.add_parser('modify',
            help='Modify an existing credential.')
        mod_parser.add_argument('name', nargs='?',
            help="The name of the credential to modify.")
        mod_parser.set_defaults(func=self.modify)
        
        args = parser.parse_args()

        self.setup(args)
        self.exit_status = args.func(args)

def main():
    main = Main()
    return main.exit_status
