import logging
import mock

from salve.log import gen_handler, clear_handlers
from salve.context import ExecutionContext

from .mockedio import MockedIO
from .context import clear_exec_context


class MockedGlobals(MockedIO):
    def __init__(self):
        MockedIO.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False

        self.patches.add(mock.patch('salve.logger', self.logger))

    def setUp(self):
        # some tests will change the log level, so set it during setUp to
        # ensure that it's always correct
        self.logger.setLevel(logging.DEBUG)
        # point the logger back at stderr
        self.logger.addHandler(gen_handler(stream=self.stderr))

        # always start tests in the startup phase
        clear_exec_context()
        ExecutionContext().transition(ExecutionContext.phases.STARTUP,
                                      quiet=True)

        MockedIO.setUp(self)

    def tearDown(self):
        MockedIO.tearDown(self)
        clear_handlers(self.logger)
