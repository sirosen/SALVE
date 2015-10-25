import logging
import mock

from salve.log import gen_handler
from salve.context import ExecutionContext

from .mockedio import MockedIO
from .context import clear_exec_context


class MockedGlobals(MockedIO):
    def __init__(self):
        MockedIO.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False

        self.logger_patch = mock.patch('salve.logger', self.logger)
        self.action_logger_patches = [
            mock.patch('salve.action.%s.logger' % loc,
                       self.logger)
            for loc in [
                'backup.file', 'backup.directory',
                'copy.file', 'create.file',
                'copy.directory', 'create.directory',
                'modify.chmod', 'modify.chown',
                'modify.file_chmod', 'modify.file_chown',
                'modify.dir_chmod', 'modify.dir_chown'
            ]
        ]

    def setUp(self):
        # some tests will change the log level, so set it during setUp to
        # ensure that it's always correct
        self.logger.setLevel(logging.DEBUG)

        # always start tests in the startup phase
        ExecutionContext().transition(ExecutionContext.phases.STARTUP,
                                      quiet=True)

        MockedIO.setUp(self)
        clear_exec_context()
        self.logger_patch.start()
        self.logger.addHandler(gen_handler(stream=self.stderr))

        for p in self.action_logger_patches:
            p.start()

    def tearDown(self):
        MockedIO.tearDown(self)
        self.logger_patch.stop()
        self.logger.handlers = []
        for p in self.action_logger_patches:
            p.stop()
