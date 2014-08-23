#!/usr/bin/python

import salve.cli.parser


def run():
    """
    Reads the commandline with a SALVE argument parser, and runs the function
    designated by the arguments.
    """
    parser = salve.cli.parser.get_parser()

    args = parser.parse_args()
    args.func(args)


def main():
    import sys

    if sys.version_info < (2, 6):
        sys.exit(1)

    run()
