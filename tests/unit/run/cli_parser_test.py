#!/usr/bin/python

import mock
import io
from nose.tools import istest

import salve.run.cli_parser as cli_parser
from tests.utils.exceptions import ensure_except


@istest
def parse_cmd1():
    """
    Command Line Parse Deploy Manifest File Specified
    Verifies that attempting to run from the commandline successfully
    parses manifest file specification in sys.argv
    """
    fake_argv = ['./salve.py', 'deploy', '-m', 'a/b/c']

    parser = cli_parser.get_parser()
    with mock.patch('sys.argv', fake_argv):
        args = parser.parse_args()
        assert args.manifest == 'a/b/c'
        assert args.directory is None
        assert args.configfile is None


@istest
def parse_cmd2():
    """
    Command Line Parse Deploy Config File Other Order
    Verifies that attempting to run from the commandline successfully
    parses config file specification in sys.argv after the deploy subcommand
    """
    fake_argv = ['./salve.py', 'deploy', '-c', 'p/q', '-m', 'root.man']

    parser = cli_parser.get_parser()
    with mock.patch('sys.argv', fake_argv):
        args = parser.parse_args()
        assert args.configfile == 'p/q'
        assert args.directory is None
        assert args.manifest == 'root.man'


@istest
def parse_cmd3():
    """
    Command Line Parse Deploy Config Option Override
    Confirms that passsing an option to a subparser overrides the value it was
    given in the parent
    """
    fake_argv = ['./salve.py', '-c', 'a/b', 'deploy', '-c', 'p/q',
            '-m', 'root.man']

    parser = cli_parser.get_parser()
    with mock.patch('sys.argv', fake_argv):
        args = parser.parse_args()
        assert args.configfile == 'p/q'
        assert args.directory is None
        assert args.manifest == 'root.man'


@istest
def parse_cmd4():
    """
    Command Line Parse Deploy No Manifest
    Confirms that omitting the manifest option causes a hard abort.
    """
    fake_argv = ['./salve.py', 'deploy', '-c', 'p/q']
    stderr = io.StringIO()

    parser = cli_parser.get_parser()
    with mock.patch('sys.argv', fake_argv), \
         mock.patch('sys.stderr', stderr):
        ensure_except(SystemExit, parser.parse_args)
