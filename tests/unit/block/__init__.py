#!/usr/bin/python

import os
import mock

import salve.settings.config
from salve.util.context import SALVEContext, StreamContext, ExecutionContext
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
dummy_context = None
dummy_exec_context = None
dummy_stream_context = None

with mock.patch('os.path.expanduser', mock_expanduser):
    dummy_stream_context = StreamContext('no such file', -1)
    dummy_exec_context = ExecutionContext()
    dummy_context = SALVEContext(exec_context=dummy_exec_context,
            stream_context=dummy_stream_context)
    dummy_conf = salve.settings.config.SALVEConfig(dummy_context)
    dummy_exec_context.set('log_level', set())
    dummy_exec_context.set('backup_dir', '/m/n')
    dummy_exec_context.set('backup_log', '/m/n.log')

dummy_logger = Logger(dummy_exec_context)
