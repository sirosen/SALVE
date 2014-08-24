#!/usr/bin/python

import mock
import io
from nose.tools import istest

from salve.cli import parser
from tests.util import ensure_except


@istest
def parse_cmd1():
    """
    Unit: Command Line Parse Deploy Manifest File Specified
    Verifies that attempting to run from the commandline successfully
    parses manifest file specification in sys.argv
    """
    fake_argv = ['./salve.py', 'deploy', '-m', 'a/b/c']

    p = parser.get_parser()
    with mock.patch('sys.argv', fake_argv):
        args = p.parse_args()
        assert args.manifest == 'a/b/c'
        assert args.directory is None
        assert args.configfile is None


@istest
def parse_cmd2():
    """
    Unit: Command Line Parse Deploy Config File Other Order
    Verifies that attempting to run from the commandline successfully
    parses config file specification in sys.argv after the deploy subcommand
    """
    fake_argv = ['./salve.py', 'deploy', '-c', 'p/q', '-m', 'root.man']

    p = parser.get_parser()
    with mock.patch('sys.argv', fake_argv):
        args = p.parse_args()
        assert args.configfile == 'p/q'
        assert args.directory is None
        assert args.manifest == 'root.man'


@istest
def parse_cmd3():
    """
    Unit: Command Line Parse Deploy Config Option Override
    Confirms that passsing an option to a subparser overrides the value it was
    given in the parent
    """
    fake_argv = ['./salve.py', '-c', 'a/b', 'deploy', '-c', 'p/q',
            '-m', 'root.man']

    p = parser.get_parser()
    with mock.patch('sys.argv', fake_argv):
        args = p.parse_args()
        assert args.configfile == 'p/q'
        assert args.directory is None
        assert args.manifest == 'root.man'


@istest
def parse_cmd4():
    """
    Unit: Command Line Parse Deploy No Manifest
    Confirms that omitting the manifest option causes a hard abort.
    """
    fake_argv = ['./salve.py', 'deploy', '-c', 'p/q']
    stderr = io.StringIO()

    p = parser.get_parser()
    with mock.patch('sys.argv', fake_argv):
        with mock.patch('sys.stderr', stderr):
            ensure_except(SystemExit, p.parse_args)
