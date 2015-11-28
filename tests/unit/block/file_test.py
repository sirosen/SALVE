import os
import mock

from nose.tools import istest
from nose_parameterized import parameterized, param

from tests.framework import ensure_except, first_param_docfunc

from tests.unit.block import dummy_file_context, ScratchWithExecCtx
from .helpers import (
    check_file_backup_act, check_file_create_act,
    check_file_copy_act, check_file_chmod_act, check_file_chown_act,
    generic_check_action_list,
    assign_block_attrs
)

from salve.action import modify
from salve.exceptions import BlockException
from salve.block import FileBlock


def check_action_list_against_defaults(actions, action_names):
    generic_check_action_list(
        actions, action_names,
        {'copy': check_file_copy_act,
         'create': check_file_create_act,
         'backup': check_file_backup_act,
         'chmod': check_file_chmod_act,
         'chown': check_file_chown_act},
        modify.FileChmodAction)


def make_file_block(mode='600', **kwargs):
    return assign_block_attrs(FileBlock(dummy_file_context),
                              mode=mode, **kwargs)


class TestWithScratchdir(ScratchWithExecCtx):
    @parameterized.expand(
        [param('Unit: File Block Copy Compile',
               ['backup', 'copy', 'chown_or_chmod', 'chown_or_chmod'],
               True, True),
         param('Unit: File Block Create Compile',
               ['create', 'chown_or_chmod', 'chown_or_chmod'],
               False, True, action='create'),
         param('Unit: File Block Copy Without User Skips Chown',
               ['backup', 'copy', 'chmod'], True, True, user=None),
         param('Unit: File Block Create Without User Skips Chown',
               ['create', 'chmod'], True, False, action='create', user=None),
         param('Unit: File Block Copy Without Group Skips Chown',
               ['backup', 'copy', 'chmod'], True, False, group=None),
         param('Unit: File Block Create Without Group Skips Chown',
               ['create', 'chmod'], True, False, action='create', group=None),
         param('Unit: File Block Copy Without Mode Skips Chmod',
               ['backup', 'copy', 'chown'], False, False, mode=None),
         param('Unit: File Block Create Without Mode Skips Chmod',
               ['create', 'chown'], False, False, action='create', mode=None),
         ],
        testcase_func_doc=first_param_docfunc)
    @istest
    def check_against_defaults(self, description, expected_al,
                               isroot, fexists, **kwargs):

        with mock.patch('salve.ugo.is_root', lambda f: isroot):
            with mock.patch('os.path.exists', lambda f: fexists):
                act = make_file_block(**kwargs).compile()
                check_action_list_against_defaults(act, expected_al)

    @parameterized.expand(
        [param('Unit: File Block Copy Compilation Fails Without Source',
               source=None),
         param('Unit: File Block Copy Compilation Fails Without Target',
               target=None),
         param('Unit: File Block Create Compilation Fails Without Target',
               action='create', target=None),
         ],
        testcase_func_doc=first_param_docfunc)
    @istest
    def compilation_blockexception(self, description, **kwargs):
        b = make_file_block(**kwargs)
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
