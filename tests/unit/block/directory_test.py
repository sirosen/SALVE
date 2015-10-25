import os
import mock
from nose.tools import istest

from tests.util import ensure_except, disambiguate_by_class

from salve.action import modify
from salve.exceptions import BlockException

from salve.block import DirBlock

from tests.unit.block import dummy_file_context, ScratchWithExecCtx
from .helpers import (
    check_list_act, check_dir_create_act,
    check_dir_chown_act, check_dir_chmod_act,

    check_file_backup_act, check_file_copy_act,
    assign_block_attrs
)


def check_actions_against_defaults(create=None, chmod=None, chown=None,
                                   chown_chmod_pair=None):
    if chown_chmod_pair:
        chmod, chown = disambiguate_by_class(
            modify.DirChmodAction, chown_chmod_pair[0], chown_chmod_pair[1])

    if create:
        check_dir_create_act(create, '/p/q/r')
    if chmod:
        check_dir_chmod_act(chmod, '755', '/p/q/r')
    if chown:
        check_dir_chown_act(chown, 'user1', 'nogroup', '/p/q/r')


def make_dir_block(action='copy', source='/a/b/c', target='/p/q/r',
                   user='user1', group='nogroup', mode='755'):
    b = DirBlock(dummy_file_context)
    assign_block_attrs(b, action=action, source=source, target=target,
                       user=user, group=group, mode=mode)
    return b


class TestWithScratchdir(ScratchWithExecCtx):
    @istest
    def dir_create_compile(self):
        """
        Unit: Directory Block Create Compile
        Verifies the result of converting a Dir Block to an Action.
        """
        act = make_dir_block(action='create', mode=None).compile()

        check_list_act(act, 2)
        check_actions_against_defaults(create=act.actions[0],
                                       chown=act.actions[1])

    @istest
    def dir_create_compile_chmod(self):
        """
        Unit: Directory Block Create Compile With Chmod
        Verifies the result of converting a Dir Block to an Action when the
        Block's mode is set.
        """
        act = make_dir_block(action='create').compile()

        check_list_act(act, 3)
        check_actions_against_defaults(
            create=act.actions[0],
            chown_chmod_pair=(act.actions[1], act.actions[2]))

    @istest
    def dir_create_chown_as_root(self):
        """
        Unit: Directory Block Create Compile With Chown
        Verifies the result of converting a Dir Block to an Action when the
        user is root and the Block's user and group are set.
        """
        with mock.patch('salve.ugo.is_root', lambda: True):
            act = make_dir_block(action='create', mode=None).compile()

        check_list_act(act, 2)
        check_actions_against_defaults(create=act.actions[0],
                                       chown=act.actions[1])

    @istest
    def empty_dir_copy_compile(self):
        """
        Unit: Directory Block Copy Compile (Empty Dir)
        Verifies the result of converting a Dir Block to an Action.
        """
        with mock.patch('os.walk', lambda d: []):
            act = make_dir_block(action='copy', mode=None, user=None,
                                 group=None).compile()

        check_list_act(act, 1)
        check_actions_against_defaults(create=act.actions[0])

    @istest
    def nested_dir_copy_compile(self):
        """
        Unit: Directory Block Copy Compile (Nested Dirs)
        Verifies the result of converting a Dir Block to an Action.
        """
        def mock_os_walk(dirname):
            return [
                (dirname, ['subdir1', 'subdir2'], ['file1']),
                (os.path.join(dirname, 'subdir1'), ['subdir3'], ['file2']),
                (os.path.join(dirname, 'subdir2'), [], []),
                (os.path.join(dirname, 'subdir1', 'subdir3'), [], ['file3'])
                ]

        def _check_file_act(fileact, fpath):
            src = os.path.join('/a/b/c', fpath)
            dst = os.path.join('/p/q/r', fpath)
            check_list_act(fileact, 2)
            check_file_backup_act(fileact.actions[0], dst, '/m/n', '/m/n.log')
            check_file_copy_act(fileact.actions[1], src, dst)

        with mock.patch('os.walk', mock_os_walk):
            act = make_dir_block(mode=None, user=None, group=None).compile()

        # there should be seven component actions in all: four for each of the
        # directories (counting the containing dir) and three for the three
        # files
        check_list_act(act, 7)
        check_dir_create_act(act.actions[0], '/p/q/r')
        check_dir_create_act(act.actions[1], '/p/q/r/subdir1')
        check_dir_create_act(act.actions[2], '/p/q/r/subdir2')
        _check_file_act(act.actions[3], 'file1')
        check_dir_create_act(act.actions[4], '/p/q/r/subdir1/subdir3')
        _check_file_act(act.actions[5], 'subdir1/file2')
        _check_file_act(act.actions[6], 'subdir1/subdir3/file3')

    @istest
    @mock.patch('salve.ugo.is_root', lambda: True)
    @mock.patch('os.walk', lambda d: [])
    def dir_copy_chown_as_root(self):
        """
        Unit: Directory Block Copy Compile (As Root)
        Verifies the result of converting a Dir Block to an Action.
        """
        act = make_dir_block(mode=None).compile()

        check_list_act(act, 2)
        check_actions_against_defaults(create=act.actions[0],
                                       chown=act.actions[1])

    @istest
    def dir_copy_fails_nosource(self):
        """
        Unit: Directory Block Copy Fails Without Source
        Verifies that converting a Dir Block to an Action raises a
        BlockException.
        """
        b = make_dir_block(source=None)
        ensure_except(BlockException, b.compile)

    @istest
    def dir_copy_fails_notarget(self):
        """
        Unit: Directory Block Copy Compilation Fails Without Target
        Verifies that converting a Dir Block to an Action raises a
        BlockException.
        """
        b = make_dir_block(target=None)
        ensure_except(BlockException, b.compile)

    @istest
    def dir_create_fails_notarget(self):
        """
        Unit: Directory Block Create Compilation Fails Without Target
        Verifies that converting a Dir Block to an Action raises a
        BlockException.
        """
        b = make_dir_block(action='create', target=None)
        ensure_except(BlockException, b.compile)

    @istest
    def dir_path_expand(self):
        """
        Unit: Directory Block Path Expand
        Verifies the results of path expansion in a Dir block.
        """
        src_path = 'p/q/r/s'
        dst_path = 't/u/v/w/x/y/z/1/2/3/../3'
        root_dir = 'file/root/directory'

        b = make_dir_block(source=src_path, target=dst_path)
        b.expand_file_paths(root_dir)

        assert b['source'] == os.path.join(root_dir, src_path)
        assert b['target'] == os.path.join(root_dir, dst_path)

    @istest
    def dir_path_expand_fail_notarget(self):
        """
        Unit: Directory Block Path Expand Fails Without Target
        Verifies that path expansion fails when there is no "target"
        attribute.
        """
        # check that this is the case for a "create" action
        root_dir = 'file/root/directory'
        b1 = make_dir_block(action='create', target=None)
        ensure_except(BlockException, b1.expand_file_paths, root_dir)

        # check that it also holds for a "copy" action with source set
        b2 = DirBlock(dummy_file_context)
        b2 = make_dir_block(target=None)
        ensure_except(BlockException, b2.expand_file_paths, root_dir)

    @istest
    def dir_compile_fail_noaction(self):
        """
        Unit: Directory Block Compilation Fails Without Action
        Verifies that block to action conversion fails when there is no
        "action" attribute.
        """
        b = make_dir_block(action=None)
        ensure_except(BlockException, b.compile)

    @istest
    def dir_compile_fail_unknown_action(self):
        """
        Unit: Directory Block Compilation Fails Unknown Action
        Verifies that block to action conversion fails when the "action"
        attribute has an unrecognized value.
        """
        b = make_dir_block(action='UNDEFINED_ACTION')
        ensure_except(BlockException, b.compile)
