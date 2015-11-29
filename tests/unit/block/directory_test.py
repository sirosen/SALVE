import os

import mock
from nose.tools import istest, eq_
from nose_parameterized import parameterized, param
from tests.framework import ensure_except, first_param_docfunc

from tests.unit.block import dummy_file_context, ScratchWithExecCtx
from .helpers import (
    check_list_act, check_dir_create_act,
    check_dir_chown_act, check_dir_chmod_act,

    check_file_backup_act, check_file_copy_act,
    generic_check_action_list,
    assign_block_attrs
)

from salve.action import modify
from salve.exceptions import BlockException
from salve.block import DirBlock


def check_action_list_against_defaults(actions, action_names):
    generic_check_action_list(
        actions, action_names,
        {'create': check_dir_create_act,
         'chmod': check_dir_chmod_act,
         'chown': check_dir_chown_act},
        modify.DirChmodAction)


def make_dir_block(mode='755', **kwargs):
    return assign_block_attrs(DirBlock(dummy_file_context),
                              mode=mode, **kwargs)


dirblock_creation_params = [
    param('Unit: Directory Block Create Compile', ['create', 'chown'], [],
          action='create', mode=None),
    param('Unit: Directory Block Create Compile With Chmod',
          ['create', 'chown_or_chmod', 'chown_or_chmod'], [],
          action='create'),
    param('Unit: Directory Block Create Compile With Chown (As Root)',
          ['create', 'chown'], [mock.patch('salve.ugo.is_root', lambda: True)],
          action='create', mode=None),
    param('Unit: Directory Block Copy Compile (Empty Dir)', ['create'],
          [mock.patch('os.walk', lambda d: [])],
          action='copy', mode=None, user=None, group=None),
    param('Unit: Directory Block Copy Compile (As Root)', ['create', 'chown'],
          [mock.patch('salve.ugo.is_root', lambda: True),
           mock.patch('os.walk', lambda d: [])],
          mode=None),
]

dirblock_compilefail_params = [
    param('Unit: Directory Block Copy Fails Without Source', source=None),
    param('Unit: Directory Block Copy Compilation Fails Without Target',
          target=None),
    param('Unit: Directory Block Create Compilation Fails Without Target',
          action='create', target=None),
    param('Unit: Directory Block Compilation Fails Without Action',
          action=None),
    param('Unit: Directory Block Compilation Fails Unknown Action',
          action='UNDEFINED_ACTION'),
]

dirblock_pathexpand_fail_params = [
    param('Unit: Directory Block (Create) Path Expand Fails Without Target',
          action='create', target=None),
    param('Unit: Directory Block (Copy) Path Expand Fails Without Target',
          target=None),
]


class TestWithScratchdir(ScratchWithExecCtx):
    @parameterized.expand(dirblock_creation_params,
                          testcase_func_doc=first_param_docfunc)
    @istest
    def dir_compilation_parameterized(self, description, expected_al, patches,
                                      **kwargs):
        for p in patches:
            p.start()
        act = make_dir_block(**kwargs).compile()
        for p in patches:
            p.stop()

        check_action_list_against_defaults(act, expected_al)

    @parameterized.expand(dirblock_compilefail_params,
                          testcase_func_doc=first_param_docfunc)
    @istest
    def dir_compilation_fails_parameterized(self, description, **kwargs):
        b = make_dir_block(**kwargs)
        ensure_except(BlockException, b.compile)

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

        eq_(b['source'], os.path.join(root_dir, src_path))
        eq_(b['target'], os.path.join(root_dir, dst_path))

    @parameterized.expand(dirblock_pathexpand_fail_params,
                          testcase_func_doc=first_param_docfunc)
    @istest
    def dir_path_expand_fail_missingattr(self, description, **kwargs):
        """
        Verifies that path expansion fails when there are missing required
        attributes.
        """
        ensure_except(BlockException,
                      make_dir_block(**kwargs).expand_file_paths,
                      'file/root/directory')
