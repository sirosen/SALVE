#!/usr/bin/python

import src.run.cli_parser

def run():
    """
    Reads the commandline with a SALVE argument parser, and runs the function
    designated by the arguments.
    """
    parser = src.run.cli_parser.get_parser()

    args = parser.parse_args()
    args.func(args)
