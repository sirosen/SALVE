import os
import mock
from nose.tools import istest

from tests.framework import ensure_except, disambiguate_by_class

from salve.action import modify
from salve.exceptions import BlockException

from salve.block import FileBlock

from tests.unit.block import dummy_file_context, ScratchWithExecCtx
from .helpers import (
    check_list_act, check_file_backup_act, check_file_create_act,
    check_file_copy_act, check_file_chmod_act, check_file_chown_act,
    assign_block_attrs
)


def check_actions_against_defaults(actions, action_names):
    actions_with_names = zip(actions, action_names)

    modify_acts = []
    check_map = {
        'copy': check_file_copy_act,
        'create': check_file_create_act,
        'backup': check_file_backup_act,
        'chmod': check_file_chmod_act,
        'chown': check_file_chown_act,
        'chown_or_chmod': modify_acts.append
    }

    for (act, name) in actions_with_names:
        check_map[name](act)

    if modify_acts:
        chmod, chown = disambiguate_by_class(
            modify.FileChmodAction, modify_acts[0], modify_acts[1])
        check_map['chmod'](chmod)
        check_map['chown'](chown)


def make_file_block(action='copy', source='/a/b/c', target='/p/q/r',
                    user='user1', group='nogroup', mode='600'):
    b = FileBlock(dummy_file_context)
    assign_block_attrs(b, action=action, source=source, target=target,
                       user=user, group=group, mode=mode)
    return b


def _common_patchset(isroot, fexists):
    @mock.patch('os.path.exists', lambda f: isroot)
    @mock.patch('os.path.exists', lambda f: fexists)
    def wrapper(f):
        return f

    return wrapper


class TestWithScratchdir(ScratchWithExecCtx):
    @istest
    def file_copy_compile(self):
        """
        Unit: File Block Copy Compile
        Verifies the result of converting a file copy block to an action.
        """
        act = make_file_block().compile()

        check_list_act(act, 4)
        check_actions_against_defaults(
            act, ['backup', 'copy', 'chown_or_chmod', 'chown_or_chmod'])

    @istest
    @_common_patchset(False, True)
    def file_create_compile(self):
        """
        Unit: File Block Create Compile
        Verifies the result of converting a file create block to an action.
        """
        act = make_file_block(action='create').compile()

        check_list_act(act, 3)
        check_actions_against_defaults(
            act, ['create', 'chown_or_chmod', 'chown_or_chmod'])

    @istest
    @_common_patchset(True, True)
    def file_copy_nouser(self):
        """
        Unit: File Block Copy Without User Skips Chown
        Verifies that converting a file copy block to an action when the
        user attribute is unset skips the chown subaction, even as root.
        """
        act = make_file_block(user=None).compile()

        check_list_act(act, 3)
        check_actions_against_defaults(act, ['backup', 'copy', 'chmod'])

    @istest
    @_common_patchset(True, False)
    def file_create_nouser(self):
        """
        Unit: File Block Create Without User Skips Chown
        Verifies that converting a file create block to an action when the
        user attribute is unset leaves out the chown.
        """
        act = make_file_block(action='create', user=None).compile()

        check_list_act(act, 2)
        check_actions_against_defaults(act, ['create', 'chmod'])

    @istest
    @_common_patchset(True, False)
    def file_copy_nogroup(self):
        """
        Unit: File Block Copy Without Group Skips Chown
        Verifies that converting a file copy block to an action when the
        group attribute is unset leaves out the chown.
        """
        act = make_file_block(group=None).compile()

        check_list_act(act, 3)
        check_actions_against_defaults(act, ['backup', 'copy', 'chmod'])

    @istest
    @_common_patchset(True, False)
    def file_create_nogroup(self):
        """
        Unit: File Block Create Without Group Skips Chown
        Verifies that converting a file create block to an action when the
        group attribute is unset raises a BlockException.
        """
        act = make_file_block(action='create', group=None).compile()

        check_list_act(act, 2)
        check_actions_against_defaults(act, ['create', 'chmod'])

    @istest
    @_common_patchset(False, False)
    def file_copy_nomode(self):
        """
        Unit: File Block Copy Without Mode Skips Chmod
        Verifies that converting a file copy block to an action when the
        mode attribute is unset raises a BlockException.
        """
        act = make_file_block(mode=None).compile()

        check_list_act(act, 3)
        check_actions_against_defaults(act, ['backup', 'copy', 'chown'])

    @istest
    @_common_patchset(False, False)
    def file_create_nomode(self):
        """
        Unit: File Block Create Without Mode Skips Chmod
        Verifies that converting a file create block to an action when the
        mode attribute is unset raises a BlockException.
        """
        act = make_file_block(action='create', mode=None).compile()

        check_list_act(act, 2)
        check_actions_against_defaults(act, ['create', 'chown'])

    @istest
    def file_copy_fails_nosource(self):
        """
        Unit: File Block Copy Fails Without Source
        Verifies that converting a file copy block to an action when the
        source attribute is unset raises a BlockException.
        """
        b = make_file_block(source=None)

        ensure_except(BlockException, b.compile)

    @istest
    def file_copy_fails_notarget(self):
        """
        Unit: File Block Copy Compilation Fails Without Target
        Verifies that converting a file copy block to an action when the
        target attribute is unset raises a BlockException.
        """
        b = make_file_block(target=None)

        ensure_except(BlockException, b.compile)

    @istest
    def file_create_fails_notarget(self):
        """
        Unit: File Block Create Compilation Fails Without Target
        Verifies that converting a file create block to an action when the
        target attribute is unset raises a BlockException.
        """
        b = make_file_block(action='create', target=None)

        ensure_except(BlockException, b.compile)

    @istest
    def file_path_expand(self):
        """
        Unit: File Block Path Expand
        Tests the results of expanding relative paths in a File block.
        """
        source_path = 'p/q/r/s'
        target_path = 't/u/v/w/x/y/z/1/2/3/../3'
        root_dir = 'file/root/directory'

        b = make_file_block(source=source_path, target=target_path)
        b.expand_file_paths(root_dir)

        assert b['source'] == os.path.join(root_dir, source_path)
        assert b['target'] == os.path.join(root_dir, target_path)

    @istest
    def file_path_expand_fail_notarget(self):
        """
        Unit: File Block Path Expand Fails Without Target
        Verifies that a File Block with the target attribute unset raises
        a BlockException when paths are expanded.
        """
        b = make_file_block(action='create', target=None)

        ensure_except(BlockException, b.expand_file_paths,
                      'file/root/directory')
