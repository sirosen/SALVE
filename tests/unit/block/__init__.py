#!/usr/bin/python

import os
import mock

from tests.util import testfile_dir

from salve import config
from salve.context import FileContext, ExecutionContext
from salve.log import Logger


def mock_expanduser(string):
    user = os.environ['USER']
    string = string.replace('~' + user, testfile_dir)
    if string[0] == '~':
        string = testfile_dir + string[1:]
    return string


dummy_conf = None
dummy_file_context = FileContext('no such file')
dummy_exec_context = ExecutionContext()
dummy_logger = Logger(dummy_exec_context)

with mock.patch('os.path.expanduser', mock_expanduser):
    with mock.patch('salve.exec_context', dummy_exec_context):
        with mock.patch('salve.logger', dummy_logger):
            dummy_conf = config.SALVEConfig()

# must be set after conf is created, otherwise they will be overidden by
# config initialization
dummy_exec_context.set('log_level', set())
dummy_exec_context.set('backup_dir', '/m/n')
dummy_exec_context.set('backup_log', '/m/n.log')
