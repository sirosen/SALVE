import mock

from .patchbin import PatchBin

# handle Py2 vs. Py3 StringIO change
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class MockedIO(PatchBin):
    def __init__(self):
        PatchBin.__init__(self)
        # create io patches
        self.stderr = StringIO()
        self.stdout = StringIO()
        self.patches.add(mock.patch('sys.stderr', self.stderr))
        self.patches.add(mock.patch('sys.stdout', self.stdout))
