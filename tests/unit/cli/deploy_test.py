import sys
import mock

from nose.tools import istest

from salve.cli import deploy

from salve.exceptions import SALVEException, ActionException, BlockException, \
    ParsingException
from salve.context import ExecutionContext, FileContext

from tests.util import ensure_except, scratch, assert_substr


startup_v3_warning = ('STARTUP [WARNING] Deprecation Warning: --directory ' +
                      'will be removed in version 3 as ' +
                      '--version3-relative-paths becomes the default.')


class TestWithScratchdir(scratch.ScratchContainer):
    def __init__(self):
        scratch.ScratchContainer.__init__(self)
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
    def deploy_main(self):
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

            def expand_blocks(self, x, y, z):
                have_run['expand_blocks'] = True

            def compile(self):
                return MockAction()

        with mock.patch('salve.cli.deploy.ManifestBlock',
                        MockManifest):
            with mock.patch('salve.config.SALVEConfig', mock.Mock()):
                with mock.patch('salve.cli.deploy.SALVEConfig', mock.Mock()):
                    deploy.main(fake_args)

        assert have_run['action_execute']
        assert have_run['expand_blocks']

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
            except SystemExit:
                assert self.mocked_exitval == 1

        err = self.stderr.getvalue()
        expected = 'STARTUP [ERROR] no such file, line -1: message string'
        assert_substr(err, expected)

    @istest
    def deploy_block_exception(self):
        """
        Unit: Deploy Command Catch BlockException
        Checks that running the deploy main function catches and pretty
        prints any thrown BlockExceptions.
        """
        ExecutionContext().transition(ExecutionContext.phases.STARTUP,
                                      quiet=True)

        fake_args = mock.Mock()
        fake_args.manifest = 'root.manifest'

        def mock_run(root_manifest, args):
            ExecutionContext().transition(ExecutionContext.phases.PARSING)
            raise BlockException('message string', self.ctx)

        with mock.patch('salve.cli.deploy.run_on_manifest', mock_run):
            try:
                deploy.main(fake_args)
            except SystemExit:
                assert self.mocked_exitval == 1
            else:
                assert False

        err = self.stderr.getvalue()
        expected = '\n'.join((
            '[DEBUG] SALVE Execution Phase Transition [STARTUP] -> [PARSING]',
            'PARSING [ERROR] no such file, line -1: message string\n'
            ))
        assert_substr(err, expected)

    @istest
    def deploy_action_exception(self):
        """
        Unit: Deploy Command Catch ActionException
        Checks that running the deploy main function catches and pretty
        prints any thrown ActionExceptions.
        """
        ExecutionContext().transition(ExecutionContext.phases.STARTUP)

        fake_args = mock.Mock()
        fake_args.manifest = 'root.manifest'

        def mock_run(root_manifest, args):
            ExecutionContext().transition(ExecutionContext.phases.COMPILATION)
            raise ActionException('message string', self.ctx)

        with mock.patch('salve.cli.deploy.run_on_manifest', mock_run):
            try:
                deploy.main(fake_args)
            except SystemExit:
                assert self.mocked_exitval == 1

        err = self.stderr.getvalue()
        expected = 'COMPILATION [ERROR] no such file, line -1: message string'
        assert_substr(err, expected)

    @istest
    def deploy_tokenization_exception(self):
        """
        Unit: Deploy Command Catch TokenizationException
        Checks that running the deploy main function catches and pretty
        prints any thrown TokenizationExceptions.
        """
        from salve.exceptions import TokenizationException

        ExecutionContext().transition(ExecutionContext.phases.STARTUP)

        fake_args = mock.Mock()
        fake_args.manifest = 'root.manifest'

        def mock_run(root_manifest, args):
            ExecutionContext().transition(ExecutionContext.phases.PARSING)
            raise TokenizationException('message string', self.ctx)

        with mock.patch('salve.cli.deploy.run_on_manifest', mock_run):
            try:
                deploy.main(fake_args)
            except SystemExit:
                assert self.mocked_exitval == 1

        err = self.stderr.getvalue()
        expected = "PARSING [ERROR] no such file, line -1: message string"
        assert_substr(err, expected)

    @istest
    def deploy_parsing_exception(self):
        """
        Unit: Deploy Command Catch ParsingException
        Checks that running the deploy main function catches and pretty
        prints any thrown ParsingExceptions.
        """
        ExecutionContext().transition(ExecutionContext.phases.STARTUP)

        fake_args = mock.Mock()
        fake_args.manifest = 'root.manifest'

        def mock_run(root_manifest, args):
            ExecutionContext().transition(ExecutionContext.phases.PARSING)
            raise ParsingException('message string', self.ctx)

        with mock.patch('salve.cli.deploy.run_on_manifest', mock_run):
            try:
                deploy.main(fake_args)
            except SystemExit:
                assert self.mocked_exitval == 1

        err = self.stderr.getvalue()
        expected = 'PARSING [ERROR] no such file, line -1: message string'
        assert_substr(err, expected)

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
