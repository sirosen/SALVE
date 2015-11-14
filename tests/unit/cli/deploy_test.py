import mock

from nose.tools import istest

from salve.cli import deploy

from salve.exceptions import (SALVEException, ActionException, BlockException,
                              ParsingException, TokenizationException)

from salve.context import ExecutionContext, FileContext

from tests.util import (ensure_except, ensure_SystemExit_with_code,
                        scratch, assert_substr)


startup_v3_warning = ('STARTUP [WARNING] Deprecation Warning: --directory ' +
                      'will be removed in version 3 as ' +
                      '--version3-relative-paths becomes the default.')


class TestWithScratchdir(scratch.ScratchContainer):
    def __init__(self):
        scratch.ScratchContainer.__init__(self)
        dummy_file_context = FileContext('no such file', -1)
        self.ctx = dummy_file_context

    @istest
    @mock.patch('salve.config.SALVEConfig')
    @mock.patch('salve.cli.deploy.ManifestBlock')
    def deploy_main(self, mock_man, mock_config):
        """
        Unit: Deploy Command Dummy Manifest Block Expand And Run
        Checks that running the deploy main function expands and runs
        a dummy manifest block with the root manifest as the source.
        """
        fake_args = mock.Mock()
        fake_args.manifest = 'root.manifest'
        fake_args.directory = '.'

        mock_action = mock.Mock()
        mock_man_instance = mock.Mock()
        mock_man_instance.compile.return_value = mock_action
        mock_man.return_value = mock_man_instance

        deploy.main(fake_args)

        assert mock_action.called
        assert mock_man_instance.expand_blocks.called

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
            ensure_SystemExit_with_code(1, deploy.main, fake_args)

        assert_substr(self.stderr.getvalue(),
                      'STARTUP [ERROR] no such file, line -1: message string')

    @istest
    def deploy_block_exception(self):
        """
        Unit: Deploy Command Catch BlockException
        Checks that running the deploy main function catches and pretty
        prints any thrown BlockExceptions.
        """
        fake_args = mock.Mock()
        fake_args.manifest = 'root.manifest'

        def mock_run(root_manifest, args):
            ExecutionContext().transition(ExecutionContext.phases.PARSING)
            raise BlockException('message string', self.ctx)

        with mock.patch('salve.cli.deploy.run_on_manifest', mock_run):
            ensure_SystemExit_with_code(1, deploy.main, fake_args)

        err = self.stderr.getvalue()
        assert_substr(err, ('[DEBUG] SALVE Execution Phase Transition ' +
                            '[STARTUP] -> [PARSING]'))
        assert_substr(err, ('PARSING [ERROR] no such file, ' +
                            'line -1: message string'))

    @istest
    def deploy_action_exception(self):
        """
        Unit: Deploy Command Catch ActionException
        Checks that running the deploy main function catches and pretty
        prints any thrown ActionExceptions.
        """
        fake_args = mock.Mock()
        fake_args.manifest = 'root.manifest'

        def mock_run(root_manifest, args):
            ExecutionContext().transition(ExecutionContext.phases.COMPILATION)
            raise ActionException('message string', self.ctx)

        with mock.patch('salve.cli.deploy.run_on_manifest', mock_run):
            ensure_SystemExit_with_code(1, deploy.main, fake_args)

        assert_substr(
            self.stderr.getvalue(),
            'COMPILATION [ERROR] no such file, line -1: message string')

    @istest
    def deploy_tokenization_exception(self):
        """
        Unit: Deploy Command Catch TokenizationException
        Checks that running the deploy main function catches and pretty
        prints any thrown TokenizationExceptions.
        """
        fake_args = mock.Mock()
        fake_args.manifest = 'root.manifest'

        def mock_run(root_manifest, args):
            ExecutionContext().transition(ExecutionContext.phases.PARSING)
            raise TokenizationException('message string', self.ctx)

        with mock.patch('salve.cli.deploy.run_on_manifest', mock_run):
            ensure_SystemExit_with_code(1, deploy.main, fake_args)

        assert_substr(self.stderr.getvalue(),
                      "PARSING [ERROR] no such file, line -1: message string")

    @istest
    def deploy_parsing_exception(self):
        """
        Unit: Deploy Command Catch ParsingException
        Checks that running the deploy main function catches and pretty
        prints any thrown ParsingExceptions.
        """
        fake_args = mock.Mock()
        fake_args.manifest = 'root.manifest'

        def mock_run(root_manifest, args):
            ExecutionContext().transition(ExecutionContext.phases.PARSING)
            raise ParsingException('message string', self.ctx)

        with mock.patch('salve.cli.deploy.run_on_manifest', mock_run):
            ensure_SystemExit_with_code(1, deploy.main, fake_args)

        assert_substr(self.stderr.getvalue(),
                      'PARSING [ERROR] no such file, line -1: message string')

    @istest
    def deploy_unexpected_exception(self):
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
