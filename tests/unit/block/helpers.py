import logging
import os

from salve import action
from salve.action import backup, create, modify, copy
from salve.context import ExecutionContext

from tests.framework import testfile_dir, scratch, disambiguate_by_class


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
    # assign attrs from the default mapping if they are not being passed
    # explicitly
    # it's not necessarily sufficient to assign and then overwrite them, as it
    # may be that an attr is passed as 'None' to indicate that it should not be
    # assigned at all, even to a None value
    shared_defaults = {
        'action': 'copy',
        'source': '/a/b/c',
        'target': '/p/q/r',
        'user': 'user1',
        'group': 'nogroup'
    }
    for k, v in shared_defaults.items():
        if k not in kwargs:
            block[k] = v

    for k, v in kwargs.items():
        if v:
            block[k] = v

    return block


def _generic_check_act(act, klass, attrs):
    assert isinstance(act, klass)
    for k, v in attrs.items():
        assert act.__getattribute__(k) == v, act.__getattribute__(k)


def check_list_act(act, list_len):
    _generic_check_act(act, action.ActionList, {})
    assert len(act.actions) == list_len


def check_file_backup_act(act, src='/p/q/r', bak_dir='/m/n',
                          logfile='/m/n.log'):
    _generic_check_act(act, backup.FileBackupAction,
                       {'src': src, 'backup_dir': bak_dir, 'logfile': logfile})


def check_file_create_act(act, dst='/p/q/r'):
    _generic_check_act(act, create.FileCreateAction, {'dst': dst})


def check_file_copy_act(act, src='/a/b/c', dst='/p/q/r'):
    _generic_check_act(act, copy.FileCopyAction, {'src': src, 'dst': dst})


def check_file_chmod_act(act, mode='600', target='/p/q/r'):
    _generic_check_act(act, modify.FileChmodAction, {'target': target})
    assert '{0:o}'.format(act.mode) == mode, str(act.mode)


def check_file_chown_act(act, user='user1', group='nogroup', target='/p/q/r'):
    _generic_check_act(act, modify.FileChownAction,
                       {'user': user, 'group': group, 'target': target})


def check_dir_create_act(act, dst='/p/q/r'):
    _generic_check_act(act, create.DirCreateAction, {'dst': dst})


def check_dir_chown_act(act, user='user1', group='nogroup', target='/p/q/r'):
    _generic_check_act(act, modify.DirChownAction,
                       {'user': user, 'group': group, 'target': target})


def check_dir_chmod_act(act, mode='755', target='/p/q/r'):
    _generic_check_act(act, modify.DirChmodAction, {'target': target})
    assert '{0:o}'.format(act.mode) == mode, str(act.mode)


def generic_check_action_list(actions, action_names, check_map, chmod_class):
    # special handling for the one-action case, in which we might or might not
    # see an ActionList
    if len(action_names) is 1 and not isinstance(actions, action.ActionList):
        check_map[action_names[0]](actions)
        return

    check_list_act(actions, len(action_names))
    actions_with_names = zip(actions, action_names)

    modify_acts = []
    check_map['chown_or_chmod'] = modify_acts.append

    for (act, name) in actions_with_names:
        check_map[name](act)

    if modify_acts:
        assert len(modify_acts) is 2
        chmod, chown = disambiguate_by_class(
            chmod_class, modify_acts[0], modify_acts[1])
        check_map['chmod'](chmod)
        check_map['chown'](chown)
