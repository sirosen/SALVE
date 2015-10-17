import logging
import os
import mock

from tests.util import testfile_dir, scratch

from salve import config
from salve.context import FileContext, ExecutionContext
from salve.log import create_logger


class ScratchWithExecCtx(scratch.ScratchContainer):
    def setUp(self):
        scratch.ScratchContainer.setUp(self)
        ExecutionContext()['log_level'] = logging.DEBUG
        ExecutionContext()['backup_dir'] = '/m/n'
        ExecutionContext()['backup_log'] = '/m/n.log'


def mock_expanduser(string):
    user = os.environ['USER']
    string = string.replace('~' + user, testfile_dir)
    if string[0] == '~':
        string = testfile_dir + string[1:]
    return string


dummy_conf = None
dummy_file_context = FileContext('no such file')
dummy_logger = create_logger(__name__)
dummy_logger.handlers = [logging.NullHandler()]

with mock.patch('os.path.expanduser', mock_expanduser):
    with mock.patch('salve.logger', dummy_logger):
        dummy_conf = config.SALVEConfig()
