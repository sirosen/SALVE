#!/usr/bin/python

import os
import sys
import StringIO
import mock

from nose.tools import istest
from unittest import SkipTest
from tests.utils.exceptions import ensure_except

import src.run.command as command
import src.util.locations as locations

from src.block.base import BlockException
from src.util.error import SALVEException, StreamContext

dummy_context = StreamContext('no such file',-1)

@istest
def no_manifest_error():
    """
    Command Line No Manifest Fails
    Verifies that attempting to run from the commandline fails if there
    is no manifest specified.
    """
    mock_opts = mock.Mock()
    mock_opts.manifest = None
    mock_opts.gitrepo = None
    optparser = mock.Mock()
    optparser.parse_args = lambda: (mock_opts,mock.Mock())

    # Patch this function to make sure the typical works
    with mock.patch('src.run.command.get_option_parser',lambda:optparser):
        ensure_except(KeyError,command.read_commandline)

    # Try this with an explicit optparser, should be the same as above
    ensure_except(KeyError,command.read_commandline,optparser)

@istest
def read_cmd_no_manifest():
    """
    Command Line No Manifest Fails On ARGV
    Verifies that attempting to run from the commandline fails if there
    is no manifest specified using sys.argv
    """
    fake_argv = ['./salve.py']
    with mock.patch('sys.argv',fake_argv):
        ensure_except(KeyError,command.read_commandline)

@istest
def parse_cmd1():
    """
    Command Line Parse Manifest File Specified
    Verifies that attempting to run from the commandline successfully
    parses manifest file specification in sys.argv
    """
    fake_argv = ['.salve.py','-m','a/b/c']

    parser = command.get_option_parser()
    with mock.patch('sys.argv',fake_argv):
        (opts,args) = parser.parse_args()
        assert opts.manifest == 'a/b/c'
        assert opts.fileroot is None
        assert opts.gitrepo is None
        assert opts.configfile is None

@istest
def parse_cmd2():
    """
    Command Line Parse Config File And Git Repo Specified
    Verifies that attempting to run from the commandline successfully
    parses config file and git repo specification in sys.argv
    """
    fake_argv = ['.salve.py','-c','p/q','--git-repo',
                 'git@github.com:sirosen/SALVE.git']
    parser = command.get_option_parser()
    with mock.patch('sys.argv',fake_argv):
        (opts,args) = parser.parse_args()
        assert opts.configfile == 'p/q'
        assert opts.gitrepo == 'git@github.com:sirosen/SALVE.git'
        assert opts.fileroot is None
        assert opts.manifest is None

@istest
def get_root_given_manifest():
    """
    Command Line Get Root Manifest Given Manifest
    Verifies that attempting to run from the commandline selects the
    specified manifest when it is part of the commandline arguments.
    """
    mock_opts = mock.Mock()
    mock_opts.manifest = '/a/b/c'
    mock_opts.gitrepo = None

    root = command.get_root_manifest(mock_opts)
    assert root == '/a/b/c'

@istest
def get_root_given_gitrepo():
    """
    Command Line Get Root Manifest Given Git Repo
    Verifies that attempting to run from the commandline selects the
    specified git repo's "root.manifest" when it is part of the
    commandline arguments and there is no "manifest" option.
    """
    mock_opts = mock.Mock()
    mock_opts.manifest = None
    mock_opts.gitrepo = 'https://github.com/sirosen/SALVE'

    ensure_except(StandardError,command.get_root_manifest,mock_opts)

@istest
def commandline_gitrepo_manifest_conflict():
    """
    Command Line Manifest Git Repo Option Conflict Fails
    Checks that running with the git repo option and manifest option
    together results in an error being thrown.
    """
    fake_argv = ['.salve.py','--git-repo',
                 'git@githubcom:sirosen/SALVE.git',
                 '--manifest','root.manifest']
    fake_stderr = StringIO.StringIO()
    with mock.patch('sys.argv',fake_argv), \
         mock.patch('sys.stderr',fake_stderr):
        command.read_commandline()
        stderr_out = fake_stderr.getvalue()
        assert stderr_out == 'Ambiguous arguments: given a git '+\
            'repo and a manifest and therefore choosing the '+\
            'manifest.\n'

@istest
def commandline_main():
    """
    Command Line Main Dummy Manifest Block Expand And Run
    Checks that running the commandline main function expands and runs
    a dummy manifest block with the root manifest as the source.
    """
    fake_argv = ['.salve.py','--manifest','root.manifest']
    have_run = {
        'action_execute': False,
        'expand_blocks': False
    }
    class MockAction(object):
        def __init__(self): pass
        def __call__(self): self.execute()
        def execute(self): have_run['action_execute'] = True

    class MockManifest(object):
        def __init__(self,source=None): assert source == 'root.manifest'
        def expand_blocks(self,x,y): have_run['expand_blocks'] = True
        def to_action(self): return MockAction()

    with mock.patch('src.block.manifest_block.ManifestBlock',MockManifest), \
         mock.patch('sys.argv',fake_argv):
        command.main()

    assert have_run['action_execute']
    assert have_run['expand_blocks']

@istest
def commandline_salve_exception():
    """
    Command Line Main Catch SALVE Exception
    Checks that running the commandline main function catches and pretty
    prints any thrown SALVEExceptions.
    """
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

    with mock.patch('src.run.command.read_commandline',lambda: (None,None)), \
         mock.patch('src.run.command.get_root_manifest',
                   mock_get_root_manifest), \
         mock.patch('src.run.command.run_on_manifest',mock_run), \
         mock.patch('sys.stderr',fake_stderr), \
         mock.patch('sys.exit',mock_exit):
        try:
            command.main()
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'SALVEException\nno such file, line -1: message string\n'

@istest
def commandline_block_exception():
    """
    Command Line Main Catch BlockException
    Checks that running the commandline main function catches and pretty
    prints any thrown BlockExceptions.
    """
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

    with mock.patch('src.run.command.read_commandline',lambda: (None,None)), \
         mock.patch('src.run.command.get_root_manifest',
                    mock_get_root_manifest), \
         mock.patch('src.run.command.run_on_manifest',mock_run), \
         mock.patch('sys.stderr',fake_stderr), \
         mock.patch('sys.exit',mock_exit):
        try:
            command.main()
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'BlockException\nno such file, line -1: message string\n'

@istest
def commandline_action_exception():
    """
    Command Line Main Catch ActionException
    Checks that running the commandline main function catches and pretty
    prints any thrown ActionExceptions.
    """
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

    with mock.patch('src.run.command.read_commandline',lambda: (None,None)),\
         mock.patch('src.run.command.get_root_manifest',
                    mock_get_root_manifest), \
         mock.patch('src.run.command.run_on_manifest',mock_run), \
         mock.patch('sys.stderr',fake_stderr), \
         mock.patch('sys.exit',mock_exit):
        try:
            command.main()
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'ActionException\nno such file, line -1: message string\n'

@istest
def commandline_tokenization_exception():
    """
    Command Line Main Catch TokenizationException
    Checks that running the commandline main function catches and pretty
    prints any thrown TokenizationExceptions.
    """
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

    with mock.patch('src.run.command.read_commandline',lambda: (None,None)), \
         mock.patch('src.run.command.get_root_manifest',
                    mock_get_root_manifest), \
         mock.patch('src.run.command.run_on_manifest',mock_run), \
         mock.patch('sys.stderr',fake_stderr), \
         mock.patch('sys.exit',mock_exit):
        try:
            command.main()
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'TokenizationException\nno such file, line -1: message string\n'

@istest
def commandline_parsing_exception():
    """
    Command Line Main Catch ParsingException
    Checks that running the commandline main function catches and pretty
    prints any thrown ParsingExceptions.
    """
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

    with mock.patch('src.run.command.read_commandline',lambda: (None,None)), \
         mock.patch('src.run.command.get_root_manifest',
                    mock_get_root_manifest), \
         mock.patch('src.run.command.run_on_manifest',mock_run), \
         mock.patch('sys.stderr',fake_stderr), \
         mock.patch('sys.exit',mock_exit):
        try:
            command.main()
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'ParsingException\nno such file, line -1: message string\n'

@istest
def commandline_unexpected_exception():
    """
    Command Line Main Don't Catch Unexpected Exception
    Checks that running the commandline main function does not catch any
    non-SALVE Exceptions.
    """
    def mock_get_root_manifest(opts):
        return None
    def mock_run(root_manifest,opts):
        raise StandardError()

    with mock.patch('src.run.command.read_commandline',lambda: (None,None)), \
         mock.patch('src.run.command.get_root_manifest',
                    mock_get_root_manifest), \
         mock.patch('src.run.command.run_on_manifest',mock_run):
        ensure_except(StandardError,command.main)
