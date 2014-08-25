#!/usr/bin/python

import os
import sys
import mock

from nose.tools import istest

from salve.cli import deploy

from salve.block import BlockException
from salve.exception import SALVEException
from salve.context import ExecutionContext, FileContext

from tests.util import ensure_except, scratch


@istest
def no_manifest_error():
    """
    Unit: Deploy Command No Manifest Fails
    Verifies that attempting to run the deploy command fails if there
    is no manifest specified.
    """
    mock_args = mock.Mock()
    mock_args.manifest = None

    ensure_except(AssertionError, deploy.main, mock_args)


@istest
def deploy_main():
    """
    Unit: Deploy Command Dummy Manifest Block Expand And Run
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

        def __call__(self, filesys):
            self.execute(filesys)

        def execute(self, filesys):
            have_run['action_execute'] = True

    class MockManifest(object):
        def __init__(self, exec_context, source=None):
            assert source == 'root.manifest'

        def expand_blocks(self, x, y):
            have_run['expand_blocks'] = True

        def compile(self):
            return MockAction()

    with mock.patch('salve.block.manifest_block.ManifestBlock', MockManifest):
        with mock.patch('salve.config.SALVEConfig', mock.Mock()):
            deploy.main(fake_args)

    assert have_run['action_execute']
    assert have_run['expand_blocks']


class TestWithScratchdir(scratch.ScratchContainer):
    def __init__(self):
        scratch.ScratchContainer.__init__(self)
        self.exec_context.set('log_level', set(('WARN', 'ERROR')))
        dummy_file_context = FileContext('no such file', -1)
        self.ctx = dummy_file_context

        self.mocked_exitval = None
        real_exit = sys.exit

        def mock_exit(n):
            self.mocked_exitval = n
            real_exit(n)

        self.exit_patch = mock.patch('sys.exit', mock_exit)

    def setUp(self):
        scratch.ScratchContainer.setUp(self)
        self.exit_patch.start()

    def tearDown(self):
        scratch.ScratchContainer.tearDown(self)
        self.exit_patch.stop()

    @istest
    def deploy_salve_exception(self):
        """
        Unit: Deploy Command Catch SALVE Exception
        Checks that running the deploy main function catches and pretty
        prints any thrown SALVEExceptions.
        """
        fake_args = mock.Mock()
        fake_args.manifest = 'root.manifest'

        def mock_run(root_manifest, args):
            raise SALVEException('message string', self.ctx)

        with mock.patch('salve.cli.deploy.run_on_manifest', mock_run):
            try:
                deploy.main(fake_args)
            except SystemExit as e:
                assert self.mocked_exitval == 1

        stderr_out = self.stderr.getvalue()
        assert stderr_out == ('[ERROR] [STARTUP] no such file, line -1: ' +
                              'message string\n')

    @istest
    def deploy_block_exception(self):
        """
        Unit: Deploy Command Catch BlockException
        Checks that running the deploy main function catches and pretty
        prints any thrown BlockExceptions.
        """
        self.exec_context.transition(ExecutionContext.phases.PARSING)

        fake_args = mock.Mock()
        fake_args.manifest = 'root.manifest'

        def mock_run(root_manifest, args):
            raise BlockException('message string', self.ctx)

        with mock.patch('salve.cli.deploy.run_on_manifest', mock_run):
            try:
                deploy.main(fake_args)
            except SystemExit as e:
                assert self.mocked_exitval == 1

        stderr_out = self.stderr.getvalue()
        assert stderr_out == ('[ERROR] [PARSING] no such file, line -1: ' +
                              'message string\n')

    @istest
    def deploy_action_exception(self):
        """
        Unit: Deploy Command Catch ActionException
        Checks that running the deploy main function catches and pretty
        prints any thrown ActionExceptions.
        """
        from salve.action import ActionException

        self.exec_context.transition(ExecutionContext.phases.COMPILATION)

        fake_args = mock.Mock()
        fake_args.manifest = 'root.manifest'

        def mock_run(root_manifest, args):
            raise ActionException('message string', self.ctx)

        with mock.patch('salve.cli.deploy.run_on_manifest', mock_run):
            try:
                deploy.main(fake_args)
            except SystemExit as e:
                assert self.mocked_exitval == 1

        stderr_out = self.stderr.getvalue()
        assert stderr_out == ('[ERROR] [COMPILATION] ' +
            'no such file, line -1: message string\n'), stderr_out

    @istest
    def deploy_tokenization_exception(self):
        """
        Unit: Deploy Command Catch TokenizationException
        Checks that running the deploy main function catches and pretty
        prints any thrown TokenizationExceptions.
        """
        from salve.reader.tokenize import TokenizationException

        self.exec_context.transition(ExecutionContext.phases.PARSING)

        fake_args = mock.Mock()
        fake_args.manifest = 'root.manifest'

        def mock_run(root_manifest, args):
            raise TokenizationException('message string', self.ctx)

        with mock.patch('salve.cli.deploy.run_on_manifest', mock_run):
            try:
                deploy.main(fake_args)
            except SystemExit as e:
                assert self.mocked_exitval == 1

        stderr_out = self.stderr.getvalue()
        assert stderr_out == ('[ERROR] [PARSING] no such file, line -1: ' +
                'message string\n'), stderr_out

    @istest
    def deploy_parsing_exception(self):
        """
        Unit: Deploy Command Catch ParsingException
        Checks that running the deploy main function catches and pretty
        prints any thrown ParsingExceptions.
        """
        from salve.reader.parse import ParsingException

        self.exec_context.transition(ExecutionContext.phases.PARSING)

        fake_args = mock.Mock()
        fake_args.manifest = 'root.manifest'

        def mock_run(root_manifest, args):
            raise ParsingException('message string', self.ctx)

        with mock.patch('salve.cli.deploy.run_on_manifest', mock_run):
            try:
                deploy.main(fake_args)
            except SystemExit as e:
                assert self.mocked_exitval == 1

        stderr_out = self.stderr.getvalue()
        assert stderr_out == ('[ERROR] [PARSING] no such file, line -1: ' +
                'message string\n'), stderr_out


@istest
def deploy_unexpected_exception():
    """
    Unit: Deploy Command Don't Catch Unexpected Exception
    Checks that running the deploy main function does not catch any
    non-SALVE Exceptions.
    """
    def mock_run(root_manifest, args):
        raise Exception()

    fake_args = mock.Mock()
    fake_args.manifest = 'root.manifest'

    with mock.patch('salve.cli.deploy.run_on_manifest', mock_run):
        ensure_except(Exception, deploy.main, fake_args)
