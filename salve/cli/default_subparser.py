"""
The contents of this module are shamelessly stolen from ruamel's std.argparse
package: https://pypi.python.org/pypi/ruamel.std.argparse/0.6.0
Because std.argparse is MIT licensed, I'm not including licensing and copyright
information inline here -- it's available in the project's repo.

We want to do parsing with argparse, but we also want a behavior that argparse
doesn't have: defaulting to 'deploy' if no subcommand is present.

Some slight modifications have been made:
 - I've made this a function that takes a parser argument, rather than a class
   method for parsers.
 - There is no support for an 'args' kwarg
 - Simpler check for '--help' argument
 - Only slices sys.argv once, rather than once per arg (just feels cleaner to
   me)
"""

import sys
import argparse


def set_default_subparser(parser, name):
    """
    Default subparser selection. Call after setup, just before parse_args()
    """
    subparser_found = False

    opts = sys.argv[1:]

    # global help takes precedence
    if '-h' in opts or '--help' in opts:
        return

    for x in parser._subparsers._actions:
        if not isinstance(x, argparse._SubParsersAction):
            continue
        for sp_name in x._name_parser_map.keys():
            if sp_name in opts:
                subparser_found = True
    if not subparser_found:
        # insert default in first position, this implies no
        # global options without a sub_parsers specified
        sys.argv.insert(1, name)
