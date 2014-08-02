#!/usr/bin/python

import os
import mock

import salve.config
from salve.util.context import FileContext, ExecutionContext
from salve.util.log import Logger

_testfile_dir = os.path.join(os.path.dirname(__file__), 'files')


def get_full_path(filename):
    return os.path.join(_testfile_dir, filename)


def mock_expanduser(string):
    user = os.environ['USER']
    string = string.replace('~' + user, _testfile_dir)
    if string[0] == '~':
        string = _testfile_dir + string[1:]
    return string


dummy_conf = None
dummy_file_context = FileContext('no such file')
dummy_exec_context = ExecutionContext()
dummy_logger = Logger(dummy_exec_context)

with mock.patch('os.path.expanduser', mock_expanduser):
    with mock.patch('salve.exec_context', dummy_exec_context):
        with mock.patch('salve.logger', dummy_logger):
            dummy_conf = salve.config.SALVEConfig()

# must be set after conf is created, otherwise they will be overidden by
# config initialization
dummy_exec_context.set('log_level', set())
dummy_exec_context.set('backup_dir', '/m/n')
dummy_exec_context.set('backup_log', '/m/n.log')
