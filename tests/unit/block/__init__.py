import mock

from salve import config
from salve.context import FileContext

from .helpers import ScratchWithExecCtx, mock_expanduser

dummy_conf = None
dummy_file_context = FileContext('no such file')

with mock.patch('os.path.expanduser', mock_expanduser):
    with mock.patch('salve.logger'):
        dummy_conf = config.SALVEConfig()


__all__ = [
    'ScratchWithExecCtx',
    'mock_expanduser',

    'dummy_conf',
    'dummy_file_context'
]
