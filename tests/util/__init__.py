import logging
import mock

from salve import paths
from salve.log import gen_handler
from salve.context import ExecutionContext

from tests.util.context import clear_exec_context

# handle Py2 vs. Py3 StringIO change
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


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
        self.stderr = StringIO()
        self.stdout = StringIO()
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
