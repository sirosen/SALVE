#!/usr/bin/python

import io
import mock

from salve import paths
from salve.log import Logger
from salve.context import ExecutionContext

from tests.util.context import clear_exec_context


testfile_dir = paths.pjoin(
    paths.containing_dir(__file__, depth=2),
    'testfiles')


def full_path(filename):
    return paths.pjoin(testfile_dir, filename)


def ensure_except(exception_type, func, *args, **kwargs):
    """
    Ensures that a function raises the desired exception.
    Asserts False (and therefore fails) when it does not.
    """
    try:
        func(*args, **kwargs)
        # fail if the function call succeeds
        assert False
    # return the desired exception, in case it needs to be
    # inspected by the calling context
    except exception_type as e:
        return e
    # fail if the wrong exception is raised
    else:
        assert False


class MockedIO(object):
    def __init__(self):
        # create io patches
        self.stderr = io.StringIO()
        self.stdout = io.StringIO()
        self.stderr_patch = mock.patch('sys.stderr', self.stderr)
        self.stdout_patch = mock.patch('sys.stdout', self.stdout)

    def setUp(self):
        self.stderr_patch.start()
        self.stdout_patch.start()

    def tearDown(self):
        self.stderr_patch.stop()
        self.stdout_patch.stop()


class MockedGlobals(MockedIO):
    def __init__(self):
        MockedIO.__init__(self)
        self.logger = Logger(logfile=self.stderr)
        self.logger_patch = mock.patch('salve.logger', self.logger)

    def setUp(self):
        MockedIO.setUp(self)
        clear_exec_context()
        self.logger_patch.start()

    def tearDown(self):
        MockedIO.tearDown(self)
        self.logger_patch.stop()
