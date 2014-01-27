#!/usr/bin/python

import os
import sys
import StringIO
import mock

from nose.tools import istest
from unittest import SkipTest
from tests.utils.exceptions import ensure_except

import src.run.command as command
import src.run.deploy as deploy
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
    mock_args = mock.Mock()
    mock_args.manifest = None
    mock_args.gitrepo = None

    ensure_except(KeyError,deploy.main,mock_args)

@istest
def get_root_given_manifest():
    """
    Deploy Command Get Root Manifest Given Manifest
    Verifies that attempting to run from the commandline selects the
    specified manifest when it is part of the commandline arguments.
    """
    mock_args = mock.Mock()
    mock_args.manifest = '/a/b/c'
    mock_args.gitrepo = None

    root = deploy.get_root_manifest(mock_args)
    assert root == '/a/b/c'

@istest
def get_root_given_gitrepo():
    """
    Deploy Command Get Root Manifest Given Git Repo
    Verifies that attempting to run from the commandline selects the
    specified git repo's "root.manifest" when it is part of the
    commandline arguments and there is no "manifest" option.
    """
    mock_args = mock.Mock()
    mock_args.manifest = None
    mock_args.gitrepo = 'https://github.com/sirosen/SALVE'

    ensure_except(StandardError,deploy.get_root_manifest,mock_args)

@istest
def deploy_gitrepo_manifest_conflict():
    """
    Deploy Command Manifest Git Repo Option Conflict Warning
    Checks that running deploy with the git repo option and manifest option
    together results in a warning being printed, but no error being thrown.
    """
    fake_args = mock.Mock()
    fake_args.gitrepo = 'git@githubcom:sirosen/SALVE.git'
    fake_args.manifest = 'root.manifest'

    fake_stderr = StringIO.StringIO()

    with mock.patch('sys.stderr',fake_stderr), \
         mock.patch('src.run.deploy.run_on_manifest',lambda x,y: None):
        deploy.main(fake_args)
        stderr_out = fake_stderr.getvalue()
        assert stderr_out == 'Ambiguous arguments: given a git '+\
            'repo and a manifest and therefore choosing the '+\
            'manifest.\n', stderr_out

@istest
def deploy_main():
    """
    Deploy Command Dummy Manifest Block Expand And Run
    Checks that running the deploy main function expands and runs
    a dummy manifest block with the root manifest as the source.
    """
    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'
    fake_args.gitrepo = None
    fake_args.directory = '.'

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
         mock.patch('src.settings.config.SALVEConfig',mock.Mock()):
        deploy.main(fake_args)

    assert have_run['action_execute']
    assert have_run['expand_blocks']

@istest
def deploy_salve_exception():
    """
    Deploy Command Catch SALVE Exception
    Checks that running the deploy main function catches and pretty
    prints any thrown SALVEExceptions.
    """
    log = {
        'exit': None
    }
    def mock_run(root_manifest,args):
        raise SALVEException('message string',dummy_context)

    real_exit = sys.exit
    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_stderr = StringIO.StringIO()
    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'
    fake_args.gitrepo = None

    with mock.patch('src.run.deploy.run_on_manifest',mock_run), \
         mock.patch('sys.stderr',fake_stderr), \
         mock.patch('sys.exit',mock_exit):
        try:
            deploy.main(fake_args)
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'SALVEException\nno such file, line -1: message string\n'

@istest
def deploy_block_exception():
    """
    Deploy Command Catch BlockException
    Checks that running the deploy main function catches and pretty
    prints any thrown BlockExceptions.
    """
    log = {
        'exit': None
    }
    def mock_run(root_manifest,opts):
        raise BlockException('message string',dummy_context)

    real_exit = sys.exit
    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_stderr = StringIO.StringIO()
    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'
    fake_args.gitrepo = None

    with mock.patch('src.run.deploy.run_on_manifest',mock_run), \
         mock.patch('sys.stderr',fake_stderr), \
         mock.patch('sys.exit',mock_exit):
        try:
            deploy.main(fake_args)
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'BlockException\nno such file, line -1: message string\n'

@istest
def deploy_action_exception():
    """
    Deploy Command Catch ActionException
    Checks that running the deploy main function catches and pretty
    prints any thrown ActionExceptions.
    """
    from src.execute.action import ActionException
    log = {
        'exit': None
    }
    def mock_run(root_manifest,opts):
        raise ActionException('message string',dummy_context)

    real_exit = sys.exit
    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_stderr = StringIO.StringIO()
    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'
    fake_args.gitrepo = None

    with mock.patch('src.run.deploy.run_on_manifest',mock_run), \
         mock.patch('sys.stderr',fake_stderr), \
         mock.patch('sys.exit',mock_exit):
        try:
            deploy.main(fake_args)
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'ActionException\nno such file, line -1: message string\n', stderr_out

@istest
def deploy_tokenization_exception():
    """
    Deploy Command Catch TokenizationException
    Checks that running the deploy main function catches and pretty
    prints any thrown TokenizationExceptions.
    """
    from src.reader.tokenize import TokenizationException
    log = {
        'exit': None
    }
    def mock_run(root_manifest,args):
        raise TokenizationException('message string',dummy_context)

    real_exit = sys.exit
    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_stderr = StringIO.StringIO()
    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'
    fake_args.gitrepo = None

    with mock.patch('src.run.deploy.run_on_manifest',mock_run), \
         mock.patch('sys.stderr',fake_stderr), \
         mock.patch('sys.exit',mock_exit):
        try:
            deploy.main(fake_args)
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'TokenizationException\nno such file, line -1: message string\n',stderr_out

@istest
def deploy_parsing_exception():
    """
    Deploy Command Catch ParsingException
    Checks that running the deploy main function catches and pretty
    prints any thrown ParsingExceptions.
    """
    from src.reader.parse import ParsingException
    log = {
        'exit': None
    }
    def mock_run(root_manifest,args):
        raise ParsingException('message string',dummy_context)

    real_exit = sys.exit
    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_stderr = StringIO.StringIO()
    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'
    fake_args.gitrepo = None

    with mock.patch('src.run.deploy.run_on_manifest',mock_run), \
         mock.patch('sys.stderr',fake_stderr), \
         mock.patch('sys.exit',mock_exit):
        try:
            deploy.main(fake_args)
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == 'Encountered a SALVE Exception of type '+\
        'ParsingException\nno such file, line -1: message string\n', stderr_out

@istest
def deploy_unexpected_exception():
    """
    Deploy Command Don't Catch Unexpected Exception
    Checks that running the deploy main function does not catch any
    non-SALVE Exceptions.
    """
    def mock_run(root_manifest,args):
        raise StandardError()

    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'
    fake_args.gitrepo = None

    with mock.patch('src.run.deploy.run_on_manifest',mock_run):
        ensure_except(StandardError,deploy.main,fake_args)
