#!/usr/bin/python

import os
import mock
from nose.tools import istest

from tests.utils.exceptions import ensure_except
from salve.block.base import BlockException

import salve.execute.action as action
import salve.execute.backup as backup
import salve.execute.modify as modify
import salve.execute.create as create
import salve.block.directory_block

from tests.unit.block import dummy_file_context, dummy_logger


@istest
def dir_create_compile():
    """
    Directory Block Create Compile
    Verifies the result of converting a Dir Block to an Action.
    """
    b = salve.block.directory_block.DirBlock(dummy_file_context)
    b.set('action', 'create')
    b.set('target', '/p/q/r')
    b.set('user', 'user1')
    b.set('group', 'nogroup')

    with mock.patch('salve.logger', dummy_logger):
        act = b.compile()

    assert isinstance(act, action.ActionList)
    assert len(act.actions) == 2

    mkdir = act.actions[0]
    chown = act.actions[1]
    assert isinstance(mkdir, create.DirCreateAction)
    assert isinstance(chown, modify.DirChownAction)

    assert mkdir.dst == '/p/q/r'
    assert chown.user == 'user1'
    assert chown.group == 'nogroup'
    assert chown.target == mkdir.dst


@istest
def dir_create_compile_chmod():
    """
    Directory Block Create Compile With Chmod
    Verifies the result of converting a Dir Block to an Action when the
    Block's mode is set.
    """
    b = salve.block.directory_block.DirBlock(dummy_file_context)
    b.set('action', 'create')
    b.set('target', '/p/q/r')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    b.set('mode', '755')

    with mock.patch('salve.logger', dummy_logger):
        dir_act = b.compile()

    assert isinstance(dir_act, action.ActionList)
    assert len(dir_act.actions) == 3

    mkdir = dir_act.actions[0]
    chmod = dir_act.actions[1]
    chown = dir_act.actions[2]
    assert isinstance(mkdir, create.DirCreateAction)
    assert isinstance(chmod, modify.DirChmodAction)
    assert isinstance(chown, modify.DirChownAction)

    assert mkdir.dst == '/p/q/r'
    assert chmod.target == mkdir.dst
    assert chmod.mode == int('755', 8)
    assert chown.user == 'user1'
    assert chown.group == 'nogroup'
    assert chown.target == mkdir.dst


@istest
def dir_create_chown_as_root():
    """
    Directory Block Create Compile With Chown
    Verifies the result of converting a Dir Block to an Action when the
    user is root and the Block's user and group are set.
    """
    b = salve.block.directory_block.DirBlock(dummy_file_context)
    b.set('action', 'create')
    b.set('target', '/p/q/r')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    with mock.patch('salve.util.ugo.is_root', lambda: True), \
         mock.patch('salve.logger', dummy_logger):
        dir_act = b.compile()

    assert isinstance(dir_act, action.ActionList)
    assert len(dir_act.actions) == 2
    mkdir = dir_act.actions[0]
    chown = dir_act.actions[1]

    assert isinstance(mkdir, create.DirCreateAction)
    assert isinstance(chown, modify.DirChownAction)

    assert mkdir.dst == '/p/q/r'
    assert chown.target == '/p/q/r'
    assert chown.user == 'user1'
    assert chown.group == 'nogroup'


@istest
def empty_dir_copy_compile():
    """
    Directory Block Copy Compile (Empty Dir)
    Verifies the result of converting a Dir Block to an Action.
    """
    b = salve.block.directory_block.DirBlock(dummy_file_context)
    b.set('action', 'copy')
    b.set('source', '/a/b/c')
    b.set('target', '/p/q/r')
    with mock.patch('os.walk', lambda d: []), \
         mock.patch('salve.logger', dummy_logger):
        dir_act = b.compile()

    assert isinstance(dir_act, action.ActionList)
    assert len(dir_act.actions) == 1
    mkdir_act = dir_act.actions[0]

    assert isinstance(mkdir_act, create.DirCreateAction)

    assert mkdir_act.dst == '/p/q/r'


@istest
def dir_copy_chown_as_root():
    """
    Directory Block Copy Compile (As Root)
    Verifies the result of converting a Dir Block to an Action.
    """
    b = salve.block.directory_block.DirBlock(dummy_file_context)
    b.set('action', 'copy')
    b.set('source', '/a/b/c')
    b.set('target', '/p/q/r')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    with mock.patch('salve.util.ugo.is_root', lambda: True), \
         mock.patch('os.walk', lambda d: []), \
         mock.patch('salve.logger', dummy_logger):
        al = b.compile()

    assert isinstance(al, action.ActionList)
    assert len(al.actions) == 2
    mkdir_act = al.actions[0]
    chown_act = al.actions[1]

    assert isinstance(mkdir_act, create.DirCreateAction)
    assert isinstance(chown_act, modify.DirChownAction)

    assert mkdir_act.dst == '/p/q/r'
    assert chown_act.target == '/p/q/r'
    assert chown_act.user == 'user1'
    assert chown_act.group == 'nogroup'


@istest
def dir_copy_fails_nosource():
    """
    Directory Block Copy Fails Without Source
    Verifies that converting a Dir Block to an Action raises a
    BlockException.
    """
    b = salve.block.directory_block.DirBlock(dummy_file_context)
    b.set('action', 'copy')
    b.set('target', '/p/q/r')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    b.set('mode', '755')

    with mock.patch('salve.logger', dummy_logger):
        ensure_except(BlockException, b.compile)


@istest
def dir_copy_fails_notarget():
    """
    Directory Block Copy Compilation Fails Without Target
    Verifies that converting a Dir Block to an Action raises a
    BlockException.
    """
    b = salve.block.directory_block.DirBlock(dummy_file_context)
    b.set('action', 'copy')
    b.set('source', '/a/b/c')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    b.set('mode', '755')

    with mock.patch('salve.logger', dummy_logger):
        ensure_except(BlockException, b.compile)


@istest
def dir_create_fails_notarget():
    """
    Directory Block Create Compilation Fails Without Target
    Verifies that converting a Dir Block to an Action raises a
    BlockException.
    """
    b = salve.block.directory_block.DirBlock(dummy_file_context)
    b.set('action', 'create')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    b.set('mode', '755')

    with mock.patch('salve.logger', dummy_logger):
        ensure_except(BlockException, b.compile)


@istest
def dir_path_expand():
    """
    Directory Block Path Expand
    Verifies the results of path expansion in a Dir block.
    """
    b = salve.block.directory_block.DirBlock(dummy_file_context)
    b.set('source', 'p/q/r/s')
    b.set('target', 't/u/v/w/x/y/z/1/2/3/../3')
    root_dir = 'file/root/directory'
    b.expand_file_paths(root_dir)
    source_loc = os.path.join(root_dir, 'p/q/r/s')
    assert b.get('source') == source_loc
    target_loc = os.path.join(root_dir, 't/u/v/w/x/y/z/1/2/3/../3')
    assert b.get('target') == target_loc


@istest
def dir_path_expand_fail_notarget():
    """
    Directory Block Path Expand Fails Without Target
    Verifies that path expansion fails when there is no "target"
    attribute.
    """
    b = salve.block.directory_block.DirBlock(dummy_file_context)
    b.set('action', 'create')
    b.set('user', 'user1')
    b.set('group', 'user1')
    b.set('mode', '755')
    root_dir = 'file/root/directory'
    ensure_except(BlockException, b.expand_file_paths, root_dir)


@istest
def dir_compile_fail_noaction():
    """
    Directory Block Compilation Fails Without Action
    Verifies that block to action conversion fails when there is no
    "action" attribute.
    """
    b = salve.block.directory_block.DirBlock(dummy_file_context)
    b.set('source', '/a/b/c')
    b.set('target', '/p/q/r')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    b.set('mode', '755')

    with mock.patch('salve.logger', dummy_logger):
        ensure_except(BlockException, b.compile)


@istest
def dir_compile_fail_unknown_action():
    """
    Directory Block Compilation Fails Unknown Action
    Verifies that block to action conversion fails when the "action"
    attribute has an unrecognized value.
    """
    b = salve.block.directory_block.DirBlock(dummy_file_context)
    b.set('action', 'UNDEFINED_ACTION')
    b.set('source', '/a/b/c')
    b.set('target', '/p/q/r')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    b.set('mode', '755')

    with mock.patch('salve.logger', dummy_logger):
        ensure_except(BlockException, b.compile)
