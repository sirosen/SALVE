#!/usr/bin/python

import os, StringIO, sys

from nose.tools import istest
from unittest import SkipTest
from mock import patch, Mock
from tests.utils.exceptions import ensure_except

import src.run.command as command
import src.util.locations as locations
from src.util.error import SALVEException, StreamContext

dummy_context = StreamContext('no such file',-1)

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
    mock_opts = Mock()
    mock_opts.manifest = None
    mock_opts.gitrepo = 'https://github.com/sirosen/SALVE'

    ensure_except(StandardError,command.get_root_manifest,mock_opts)

@istest
def commandline_gitrepo_manifest_conflict():
    fake_argv = ['.salve.py','--git-repo',
                 'git@githubcom:sirosen/SALVE.git',
                 '--manifest','root.manifest']
    fake_stderr = StringIO.StringIO()
    with patch('sys.argv',fake_argv):
        with patch('sys.stderr',fake_stderr):
            command.read_commandline()
            stderr_out = fake_stderr.getvalue()
            assert stderr_out == 'Ambiguous arguments: given a git '+\
                'repo and a manifest and therefore choosing the '+\
                'manifest.\n'

@istest
def commandline_main():
    fake_argv = ['.salve.py','--manifest','root.manifest']
    have_run = {
        'action_execute': False,
        'expand_blocks': False
    }
    class MockAction(object):
        def __init__(self): pass
        def execute(self): have_run['action_execute'] = True

    class MockManifest(object):
        def __init__(self,source=None): assert source == 'root.manifest'
        def expand_blocks(self,x,y): have_run['expand_blocks'] = True
        def to_action(self): return MockAction()

    with patch('src.block.manifest_block.ManifestBlock',MockManifest):
        with patch('sys.argv',fake_argv):
            command.main()

    assert have_run['action_execute']
    assert have_run['expand_blocks']

@istest
def commandline_salve_exception():
    log = {
        'exit': None
    }
    def mock_get_root_manifest(opts):
        return None
    def mock_run(root_manifest,opts):
        raise SALVEException('message string',dummy_context)

    real_exit = sys.exit
    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_stderr = StringIO.StringIO()

    with patch('src.run.command.read_commandline',lambda: (None,None)):
        with patch('src.run.command.get_root_manifest',
                   mock_get_root_manifest):
            with patch('src.run.command.run_on_manifest',mock_run):
                with patch('sys.stderr',fake_stderr):
                    with patch('sys.exit',mock_exit):
                        try:
                            command.main()
                        except SystemExit as e:
                            assert log['exit'] is not None and \
                                   log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'SALVEException\noriginating at no such file: -1\ncarrying '+\
        'a message message string\n'

@istest
def commandline_block_exception():
    from src.block.base_block import BlockException
    log = {
        'exit': None
    }
    def mock_get_root_manifest(opts):
        return None
    def mock_run(root_manifest,opts):
        raise BlockException('message string',dummy_context)

    real_exit = sys.exit
    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_stderr = StringIO.StringIO()

    with patch('src.run.command.read_commandline',lambda: (None,None)):
        with patch('src.run.command.get_root_manifest',
                   mock_get_root_manifest):
            with patch('src.run.command.run_on_manifest',mock_run):
                with patch('sys.stderr',fake_stderr):
                    with patch('sys.exit',mock_exit):
                        try:
                            command.main()
                        except SystemExit as e:
                            assert log['exit'] is not None and \
                                   log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'BlockException\noriginating at no such file: -1\ncarrying '+\
        'a message message string\n'

@istest
def commandline_action_exception():
    from src.execute.action import ActionException
    log = {
        'exit': None
    }
    def mock_get_root_manifest(opts):
        return None
    def mock_run(root_manifest,opts):
        raise ActionException('message string',dummy_context)

    real_exit = sys.exit
    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_stderr = StringIO.StringIO()

    with patch('src.run.command.read_commandline',lambda: (None,None)):
        with patch('src.run.command.get_root_manifest',
                   mock_get_root_manifest):
            with patch('src.run.command.run_on_manifest',mock_run):
                with patch('sys.stderr',fake_stderr):
                    with patch('sys.exit',mock_exit):
                        try:
                            command.main()
                        except SystemExit as e:
                            assert log['exit'] is not None and \
                                   log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'ActionException\noriginating at no such file: -1\ncarrying '+\
        'a message message string\n'

@istest
def commandline_tokenization_exception():
    from src.reader.tokenize import TokenizationException
    log = {
        'exit': None
    }
    def mock_get_root_manifest(opts):
        return None
    def mock_run(root_manifest,opts):
        raise TokenizationException('message string',dummy_context)

    real_exit = sys.exit
    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_stderr = StringIO.StringIO()

    with patch('src.run.command.read_commandline',lambda: (None,None)):
        with patch('src.run.command.get_root_manifest',
                   mock_get_root_manifest):
            with patch('src.run.command.run_on_manifest',mock_run):
                with patch('sys.stderr',fake_stderr):
                    with patch('sys.exit',mock_exit):
                        try:
                            command.main()
                        except SystemExit as e:
                            assert log['exit'] is not None and \
                                   log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'TokenizationException\noriginating at no such file: -1\n'+\
        'carrying a message message string\n'

@istest
def commandline_parsing_exception():
    from src.reader.parse import ParsingException
    log = {
        'exit': None
    }
    def mock_get_root_manifest(opts):
        return None
    def mock_run(root_manifest,opts):
        raise ParsingException('message string',dummy_context)

    real_exit = sys.exit
    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_stderr = StringIO.StringIO()

    with patch('src.run.command.read_commandline',lambda: (None,None)):
        with patch('src.run.command.get_root_manifest',
                   mock_get_root_manifest):
            with patch('src.run.command.run_on_manifest',mock_run):
                with patch('sys.stderr',fake_stderr):
                    with patch('sys.exit',mock_exit):
                        try:
                            command.main()
                        except SystemExit as e:
                            assert log['exit'] is not None and \
                                   log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'ParsingException\noriginating at no such file: -1\n'+\
        'carrying a message message string\n'

@istest
def commandline_unexpected_exception():
    def mock_get_root_manifest(opts):
        return None
    def mock_run(root_manifest,opts):
        raise StandardError()

    with patch('src.run.command.read_commandline',lambda: (None,None)):
        with patch('src.run.command.get_root_manifest',
                   mock_get_root_manifest):
            with patch('src.run.command.run_on_manifest',mock_run):
                ensure_except(StandardError,command.main)
