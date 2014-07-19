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
from src.util.error import SALVEException
from src.util.context import SALVEContext, ExecutionContext, StreamContext


def generate_dummy_context(fake_stderr, phase=ExecutionContext.phases.STARTUP):
    with mock.patch.dict('src.settings.default_globals.defaults',
                         {'run_log': fake_stderr}):
        dummy_stream_context = StreamContext('no such file', -1)
        dummy_exec_context = ExecutionContext(startphase=phase)
        dummy_exec_context.set('log_level', set(('WARN', 'ERROR')))
        return SALVEContext(stream_context=dummy_stream_context,
                            exec_context=dummy_exec_context)


@istest
def no_manifest_error():
    """
    Deploy Command No Manifest Fails
    Verifies that attempting to run the deploy command fails if there
    is no manifest specified.
    """
    mock_args = mock.Mock()
    mock_args.manifest = None

    ensure_except(AssertionError, deploy.main, mock_args)


@istest
def deploy_main():
    """
    Deploy Command Dummy Manifest Block Expand And Run
    Checks that running the deploy main function expands and runs
    a dummy manifest block with the root manifest as the source.
    """
    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'
    fake_args.directory = '.'

    have_run = {
        'action_execute': False,
        'expand_blocks': False
    }

    class MockAction(object):
        def __init__(self):
            pass

        def __call__(self):
            self.execute()

        def execute(self):
            have_run['action_execute'] = True

    class MockManifest(object):
        def __init__(self, exec_context, source=None):
            assert source == 'root.manifest'

        def expand_blocks(self, x, y):
            have_run['expand_blocks'] = True

        def compile(self):
            return MockAction()

    with mock.patch('src.block.manifest_block.ManifestBlock', MockManifest), \
         mock.patch('src.settings.config.SALVEConfig', mock.Mock()):
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

    real_exit = sys.exit

    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_stderr = StringIO.StringIO()
    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'

    dummy_context = generate_dummy_context(fake_stderr)

    def mock_run(root_manifest, exec_context, args):
        raise SALVEException('message string', dummy_context)

    with mock.patch('src.run.deploy.run_on_manifest', mock_run), \
         mock.patch('sys.exit', mock_exit):
        try:
            deploy.main(fake_args)
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == ('[ERROR] [STARTUP] no such file, line -1: ' +
                          'message string\n')


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

    real_exit = sys.exit

    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_stderr = StringIO.StringIO()
    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'

    dummy_context = generate_dummy_context(fake_stderr,
            phase=ExecutionContext.phases.PARSING)

    def mock_run(root_manifest, exec_context, args):
        raise BlockException('message string', dummy_context)

    with mock.patch('src.run.deploy.run_on_manifest', mock_run), \
         mock.patch('sys.stderr', fake_stderr), \
         mock.patch('sys.exit', mock_exit):
        try:
            deploy.main(fake_args)
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == ('[ERROR] [PARSING] no such file, line -1: ' +
                          'message string\n')


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

    real_exit = sys.exit

    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_stderr = StringIO.StringIO()
    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'

    dummy_context = generate_dummy_context(fake_stderr,
        phase=ExecutionContext.phases.COMPILATION)

    def mock_run(root_manifest, exec_context, args):
        raise ActionException('message string', dummy_context)

    with mock.patch('src.run.deploy.run_on_manifest', mock_run), \
         mock.patch('sys.exit', mock_exit):
        try:
            deploy.main(fake_args)
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == ('[ERROR] [COMPILATION] ' +
        'no such file, line -1: message string\n'), stderr_out


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

    real_exit = sys.exit

    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_stderr = StringIO.StringIO()
    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'

    dummy_context = generate_dummy_context(fake_stderr,
        phase=ExecutionContext.phases.PARSING)

    def mock_run(root_manifest, exec_context, args):
        raise TokenizationException('message string', dummy_context)

    with mock.patch('src.run.deploy.run_on_manifest', mock_run), \
         mock.patch('sys.exit', mock_exit):
        try:
            deploy.main(fake_args)
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == ('[ERROR] [PARSING] no such file, line -1: ' +
            'message string\n'), stderr_out


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

    real_exit = sys.exit

    def mock_exit(n):
        log['exit'] = n
        real_exit(n)

    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'
    fake_stderr = StringIO.StringIO()

    dummy_context = generate_dummy_context(fake_stderr,
            phase=ExecutionContext.phases.PARSING)

    def mock_run(root_manifest, context, args):
        raise ParsingException('message string', dummy_context)

    with mock.patch('src.run.deploy.run_on_manifest', mock_run), \
         mock.patch('sys.exit', mock_exit):
        try:
            deploy.main(fake_args)
        except SystemExit as e:
            assert log['exit'] is not None and \
                log['exit'] == 1

    stderr_out = fake_stderr.getvalue()
    assert stderr_out == ('[ERROR] [PARSING] no such file, line -1: ' +
            'message string\n'), stderr_out


@istest
def deploy_unexpected_exception():
    """
    Deploy Command Don't Catch Unexpected Exception
    Checks that running the deploy main function does not catch any
    non-SALVE Exceptions.
    """
    def mock_run(root_manifest, exec_context, args):
        raise StandardError()

    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'

    with mock.patch('src.run.deploy.run_on_manifest', mock_run):
        ensure_except(StandardError, deploy.main, fake_args)
