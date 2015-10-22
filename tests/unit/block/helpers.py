import logging
import os

from salve import action
from salve.action import backup, create, modify, copy
from salve.context import ExecutionContext

from tests.util import testfile_dir, scratch


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


def assign_block_attrs(block, **kwargs):
    for k, v in kwargs.items():
        if v:
            block[k] = v


def _generic_check_act(act, klass, attrs):
    assert isinstance(act, klass)
    for k, v in attrs.items():
        assert act.__getattribute__(k) == v, act.__getattribute__(k)


def check_list_act(act, list_len):
    _generic_check_act(act, action.ActionList, {})
    assert len(act.actions) == list_len


def check_file_backup_act(act, src, bak_dir, logfile):
    _generic_check_act(act, backup.FileBackupAction,
                       {'src': src, 'backup_dir': bak_dir, 'logfile': logfile})


def check_file_create_act(act, dst):
    _generic_check_act(act, create.FileCreateAction, {'dst': dst})


def check_file_copy_act(act, src, dst):
    _generic_check_act(act, copy.FileCopyAction, {'src': src, 'dst': dst})


def check_file_chmod_act(act, mode, target):
    _generic_check_act(act, modify.FileChmodAction, {'target': target})
    assert '{0:o}'.format(act.mode) == mode, str(act.mode)


def check_file_chown_act(act, user, group, target):
    _generic_check_act(act, modify.FileChownAction,
                       {'user': user, 'group': group, 'target': target})


def check_dir_create_act(act, dst):
    _generic_check_act(act, create.DirCreateAction, {'dst': dst})


def check_dir_chown_act(act, user, group, target):
    _generic_check_act(act, modify.DirChownAction,
                       {'user': user, 'group': group, 'target': target})


def check_dir_chmod_act(act, mode, target):
    _generic_check_act(act, modify.DirChmodAction, {'target': target})
    assert '{0:o}'.format(act.mode) == mode, str(act.mode)
