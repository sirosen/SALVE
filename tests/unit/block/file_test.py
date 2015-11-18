import os
import mock
from nose.tools import istest

from tests.framework import ensure_except

from salve.action import modify
from salve.exceptions import BlockException

from salve.block import FileBlock

from tests.unit.block import dummy_file_context, ScratchWithExecCtx
from .helpers import (
    check_file_backup_act, check_file_create_act,
    check_file_copy_act, check_file_chmod_act, check_file_chown_act,
    generic_check_action_list,
    assign_block_attrs
)


def check_action_list_against_defaults(actions, action_names):
    generic_check_action_list(
        actions, action_names,
        {'copy': check_file_copy_act,
         'create': check_file_create_act,
         'backup': check_file_backup_act,
         'chmod': check_file_chmod_act,
         'chown': check_file_chown_act},
        modify.FileChmodAction)


def make_file_block(action='copy', source='/a/b/c', target='/p/q/r',
                    user='user1', group='nogroup', mode='600'):
    b = FileBlock(dummy_file_context)
    assign_block_attrs(b, action=action, source=source, target=target,
                       user=user, group=group, mode=mode)
    return b


class TestWithScratchdir(ScratchWithExecCtx):
    @istest
    def check_against_defaults_generator(self):
        parameters = [
            ({},
             ['backup', 'copy', 'chown_or_chmod', 'chown_or_chmod'],
             'Unit: File Block Copy Compile',
             True, True),
            ({'action': 'create'},
             ['create', 'chown_or_chmod', 'chown_or_chmod'],
             'Unit: File Block Create Compile',
             False, True),
            ({'user': None},
             ['backup', 'copy', 'chmod'],
             'Unit: File Block Copy Without User Skips Chown',
             True, True),
            ({'action': 'create', 'user': None},
             ['create', 'chmod'],
             'Unit: File Block Create Without User Skips Chown',
             True, False),
            ({'group': None},
             ['backup', 'copy', 'chmod'],
             'Unit: File Block Copy Without Group Skips Chown',
             True, False),
            ({'action': 'create', 'group': None},
             ['create', 'chmod'],
             'Unit: File Block Create Without Group Skips Chown',
             True, False),
            ({'mode': None},
             ['backup', 'copy', 'chown'],
             'Unit: File Block Copy Without Mode Skips Chmod',
             False, False),
            ({'action': 'create', 'mode': None},
             ['create', 'chown'],
             'Unit: File Block Create Without Mode Skips Chmod',
             False, False),
        ]

        for (kwargs, expected_al, description, isroot, fexists) in parameters:
            @mock.patch('salve.ugo.is_root', lambda f: isroot)
            @mock.patch('os.path.exists', lambda f: fexists)
            def check_func():
                act = make_file_block(**kwargs).compile()
                check_action_list_against_defaults(act, expected_al)
            check_func.description = description

            yield check_func

    @istest
    def compilation_blockexception_generator(self):
        parameters = [
            ({'source': None},
             'Unit: File Block Copy Compilation Fails Without Source'),
            ({'target': None},
             'Unit: File Block Copy Compilation Fails Without Target'),
            ({'action': 'create', 'target': None},
             'Unit: File Block Create Compilation Fails Without Target'),
        ]

        for (kwargs, description) in parameters:
            def check_func():
                b = make_file_block(**kwargs)
                ensure_except(BlockException, b.compile)
            check_func.description = description

            yield check_func

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
