#!/usr/bin/python

import salve.run.cli_parser


def run():
    """
    Reads the commandline with a SALVE argument parser, and runs the function
    designated by the arguments.
    """
    parser = salve.run.cli_parser.get_parser()

    args = parser.parse_args()
    args.func(args)
