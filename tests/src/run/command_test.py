#!/usr/bin/python

import os

from nose.tools import istest
from unittest import SkipTest
from mock import patch, Mock
from tests.utils.exceptions import ensure_except

import src.run.command as command
import src.util.locations as locations

@istest
def no_manifest_error():
    mock_opts = Mock()
    mock_opts.manifest = None
    mock_opts.gitrepo = None
    optparser = Mock()
    optparser.parse_args = lambda: (mock_opts,Mock())

    # Patch this function to make sure the typical works
    with patch('src.run.command.get_option_parser',lambda:optparser):
        ensure_except(KeyError,command.read_commandline)

    # Try this with an explicit optparser, should be the same as above
    ensure_except(KeyError,command.read_commandline,optparser)

@istest
def read_cmd_no_manifest():
    fake_argv = ['./salve.py']
    with patch('sys.argv',fake_argv):
        ensure_except(KeyError,command.read_commandline)

@istest
def parse_cmd1():
    fake_argv = ['.salve.py','-m','a/b/c']

    parser = command.get_option_parser()
    with patch('sys.argv',fake_argv):
        (opts,args) = parser.parse_args()
        assert opts.manifest == 'a/b/c'
        assert opts.fileroot is None
        assert opts.gitrepo is None
        assert opts.configfile is None

@istest
def parse_cmd2():
    fake_argv = ['.salve.py','-c','p/q','--git-repo',
                 'git@github.com:sirosen/SALVE.git']
    parser = command.get_option_parser()
    with patch('sys.argv',fake_argv):
        (opts,args) = parser.parse_args()
        assert opts.configfile == 'p/q'
        assert opts.gitrepo == 'git@github.com:sirosen/SALVE.git'
        assert opts.fileroot is None
        assert opts.manifest is None

@istest
def get_root_given_manifest():
    mock_opts = Mock()
    mock_opts.manifest = '/a/b/c'
    mock_opts.gitrepo = None

    root = command.get_root_manifest(mock_opts)
    assert root == '/a/b/c'

@istest
def get_root_given_gitrepo():
    # skip for now, not implemented
    raise SkipTest
    mock_opts = Mock()
    mock_opts.manifest = None
    mock_opts.gitrepo = 'https://github.com/sirosen/SALVE'

    root = command.get_root_manifest(mock_opts)
    assert root == os.path.join(locations.get_salve_root(),
                                'root.manifest')
