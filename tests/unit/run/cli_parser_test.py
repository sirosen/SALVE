#!/usr/bin/python

import mock
from nose.tools import istest

import src.run.cli_parser as cli_parser

@istest
def parse_cmd1():
    """
    Command Line Parse Manifest File Specified
    Verifies that attempting to run from the commandline successfully
    parses manifest file specification in sys.argv
    """
    fake_argv = ['./salve.py','deploy','-m','a/b/c']

    parser = cli_parser.get_parser()
    with mock.patch('sys.argv',fake_argv):
        args = parser.parse_args()
        assert args.manifest == 'a/b/c'
        assert args.directory is None
        assert args.gitrepo is None
        assert args.configfile is None

@istest
def parse_cmd2():
    """
    Command Line Parse Config File And Git Repo Specified
    Verifies that attempting to run from the commandline successfully
    parses config file and git repo specification in sys.argv
    """
    fake_argv = ['./salve.py','-c','p/q','deploy','--git-repo',
                 'git@github.com:sirosen/SALVE.git']

    parser = cli_parser.get_parser()
    with mock.patch('sys.argv',fake_argv):
        args = parser.parse_args()
        assert args.configfile == 'p/q'
        assert args.gitrepo == 'git@github.com:sirosen/SALVE.git'
        assert args.directory is None
        assert args.manifest is None

@istest
def parse_cmd3():
    """
    Command Line Parse Config File Other Order
    Verifies that attempting to run from the commandline successfully
    parses config file specification in sys.argv after the deploy subcommand
    """
    fake_argv = ['./salve.py','deploy','-c','p/q']

    parser = cli_parser.get_parser()
    with mock.patch('sys.argv',fake_argv):
        args = parser.parse_args()
        assert args.configfile == 'p/q'
        assert args.gitrepo is None
        assert args.directory is None
        assert args.manifest is None

@istest
def parse_cmd4():
    """
    Command Line Parse Config Option Override
    Confirms that passsing an option to a subparser overrides the value it was
    given in the parent
    """
    fake_argv = ['./salve.py','-c','a/b','deploy','-c','p/q']

    parser = cli_parser.get_parser()
    with mock.patch('sys.argv',fake_argv):
        args = parser.parse_args()
        assert args.configfile == 'p/q'
        assert args.gitrepo is None
        assert args.directory is None
        assert args.manifest is None
