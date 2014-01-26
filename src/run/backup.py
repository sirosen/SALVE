#!/usr/bin/python

import optparse

def get_option_parser():
    """
    Produces a command line option parser for SALVE using optparse.
    Although argparse is significantly nicer, it's only available as
    an added package in python<2.7. Since 2.6 is in wide use at this
    time, and some distributions of 2.7 require a pip install for
    argparse, optparse is going to have to do.
    """
    option_parser = optparse.OptionParser(description="The backup subcommand "+\
        "for SALVE. Used to perform actions on the backup files including " +\
        "viewing, recovery, and deletion.")
    option_parser.add_option('-r','--recover',dest='recover',
        help='Boolean flag, indicates that recovery should be performed.',
        action='store_true',default=False)
    option_parser.add_option('-s','--show-versions',dest='show_versions',
        help='Boolean flag, indicates that the file\'s versions should be '+\
        'displayed with varying generation numbers and dates.',
        action='store_true',default=False)
    option_parser.add_option('-f','--filename',dest='filename',
        help='The absolute path to the file to act upon.')
    return option_parser

def read_commandline():
    """
    Reads the commandline with a SALVE option parser, and validates the
    inputs that were received.

    KWArgs:
        @option_parser
        A given option_parser for reading the commandline. If not given,
        or given as a non-true value, the function will generate a new
        one.
    """
    option_parser = get_option_parser()

    (opts,args) = option_parser.parse_args()

    return (opts,args)

def main():
    (opts,args) = read_commandline()
