import mock

# handle Py2 vs. Py3 StringIO change
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


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
