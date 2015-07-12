#!/usr/bin/python

from __future__ import unicode_literals
import argparse
import textwrap

import salve
import salve.cli.deploy
import salve.cli.backup


def add_backup_args(parser):  # pragma: no cover
    """
    Takes in an argparse parser and adds the options for the backup subcommand.
    This is necessary because of the way that argparse handles subparsers --
    namely, that they are created automatically at the time of addition.
    """
    parser.add_argument(
        '-r', '--recover', dest='recover', action='store_true',
        default=False,
        help='Boolean flag, indicates that recovery should be performed.')
    parser.add_argument(
        '-s', '--show-versions', dest='show_versions',
        action='store_true', default=False,
        help='Boolean flag, indicates that the file\'s versions should be ' +
        'displayed with varying generation numbers and dates.')
    parser.add_argument(
        '-f', '--filename', dest='filename', default=None,
        required=True, help='The absolute path to the file to act upon.')

    parser.set_defaults(func=salve.cli.backup.main)


def add_deploy_args(parser):
    """
    Takes in an argparse parser and adds the options for the deploy subcommand.
    This is necessary because of the way that argparse handles subparsers --
    namely, that they are created automatically at the time of addition.
    """
    parser.add_argument(
        '-m', '--manifest', dest='manifest', default=None,
        required=True, help='The root manifest file for execution.')
    parser.add_argument(
        '-d', '--directory', dest='directory', default=None,
        help='The directory to which relative paths in manifests refer. ' +
        'Will be removed in version 3.')
    parser.add_argument(
        '--ver3', '--version3', dest='version3',
        default=False, action='store_true', help='Enable version 3 mode ' +
        '(turn on all options which will become defaults in version 3).')
    parser.add_argument(
        '--version3-relative-paths', dest='v3_relpath',
        default=False, action='store_true', help='Expand relative paths ' +
        'in manifests relative to the current manifest, rather than ' +
        'the root manifest.')

    parser.set_defaults(func=salve.cli.deploy.main)


def get_parser():
    """
    Produces a command line option parser for SALVE using argparse.

    We only support Python 2.6 when argparse is installed.
    """
    class SALVESharedParser(argparse.ArgumentParser):
        def __init__(self, *args, **kwargs):
            argparse.ArgumentParser.__init__(self, *args, **kwargs)
            self.add_argument(
                '-c', '--config-file', dest='configfile',
                default=None, help='A SALVE config file (INI format).')
            self.add_argument(
                '-v', '--verbose', dest='verbosity',
                default=0, action='count', help='Verbosity of log output. ' +
                'Specify multiple times for higher verbosity.')
            self.add_argument(
                '--version', action='version',
                version="%(prog)s " + salve.__version__)

    description = textwrap.dedent("""Run a SALVE command.
        SALVE is a configuration deployment language that guarantees the
        properties of idempotence, safety, and recoverability that are
        necessary in order to manage personal configuration files in a
        straightforward way.
        For a full description of SALVE and its capabilities, visit
        http://salve.sirosen.net/""")

    parser = SALVESharedParser(prog='SALVE', description=description)

    subparsers = parser.add_subparsers(
        title='Subcommands',
        parser_class=SALVESharedParser, metavar='')

    # don't yet add the backup parser -- it isn't supported yet
    # backup_parser = subparsers.add_parser('backup',
    #         help='Directly manipulate, inspect, and restore from backups.')
    # add_backup_args(backup_parser)

    deploy_parser = subparsers.add_parser(
        'deploy', help='Run on a manifest' +
        ' tree and deploy the described configuration.')
    add_deploy_args(deploy_parser)

    return parser
