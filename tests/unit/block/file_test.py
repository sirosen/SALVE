#!/usr/bin/python

import os
import mock
from nose.tools import istest

from tests.utils.exceptions import ensure_except
from src.block.base import BlockException
from src.util.context import SALVEContext, ExecutionContext

import src.execute.action as action
import src.execute.backup as backup
import src.execute.create as create
import src.execute.modify as modify
import src.execute.copy as copy
import src.block.file_block

dummy_exec_context = ExecutionContext()
dummy_exec_context.set('backup_dir', '/m/n')
dummy_exec_context.set('backup_log', '/m/n.log')
dummy_exec_context.set('log_level', set())
dummy_context = SALVEContext(exec_context=dummy_exec_context)


@istest
def file_copy_to_action():
    """
    File Block Copy To Action
    Verifies the result of converting a file copy block to an action.
    """
    b = src.block.file_block.FileBlock(dummy_context)
    b.set('action', 'copy')
    b.set('source', '/a/b/c')
    b.set('target', '/p/q/r')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    b.set('mode', '600')

    act = b.to_action()

    assert isinstance(act, action.ActionList)
    assert len(act.actions) == 4
    backup_act = act.actions[0]
    copy_act = act.actions[1]
    mod_act1 = act.actions[2]
    mod_act2 = act.actions[3]

    if isinstance(mod_act1, modify.FileChmodAction):
        chmod_act = mod_act1
        chown_act = mod_act2
    else:
        chown_act = mod_act1
        chmod_act = mod_act2

    assert isinstance(backup_act, backup.FileBackupAction)
    assert isinstance(copy_act, copy.FileCopyAction)
    assert isinstance(chmod_act, modify.FileChmodAction)
    assert isinstance(chown_act, modify.FileChownAction)

    assert backup_act.backup_dir == '/m/n'
    assert backup_act.logfile == '/m/n.log'
    assert copy_act.src == '/a/b/c'
    assert copy_act.dst == '/p/q/r'
    assert '{0:o}'.format(chmod_act.mode) == '600'
    assert chmod_act.target == copy_act.dst
    assert chown_act.user == 'user1'
    assert chown_act.group == 'nogroup'
    assert chown_act.target == copy_act.dst


@istest
def file_create_to_action():
    """
    File Block Create To Action
    Verifies the result of converting a file create block to an action.
    """
    b = src.block.file_block.FileBlock(dummy_context)
    b.set('action', 'create')
    b.set('target', '/p/q/r')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    b.set('mode', '0600')
    with mock.patch('os.path.exists', lambda f: True), \
         mock.patch('src.util.ugo.is_root', lambda: False):
        file_act = b.to_action()

    assert isinstance(file_act, action.ActionList)
    assert len(file_act.actions) == 3

    touch = file_act.actions[0]

    mod_act1 = file_act.actions[1]
    mod_act2 = file_act.actions[2]

    if isinstance(mod_act1, modify.FileChmodAction):
        chmod_act = mod_act1
        chown_act = mod_act2
    else:
        chown_act = mod_act1
        chmod_act = mod_act2

    assert isinstance(touch, create.FileCreateAction)
    assert isinstance(chmod_act, modify.FileChmodAction)
    assert isinstance(chown_act, modify.FileChownAction)

    assert touch.dst == '/p/q/r'
    assert chmod_act.target == '/p/q/r'
    assert chown_act.user == 'user1'
    assert chown_act.group == 'nogroup'
    assert chown_act.target == touch.dst


@istest
def file_copy_nouser():
    """
    File Block Copy Without User Skips Chown
    Verifies that converting a file copy block to an action when the
    user attribute is unset skips the chown subaction, even as root.
    """
    b = src.block.file_block.FileBlock(dummy_context)
    b.set('action', 'copy')
    b.set('source', '/a/b/c')
    b.set('target', '/p/q/r')
    b.set('group', 'nogroup')
    b.set('mode', '0600')

    with mock.patch('src.util.ugo.is_root', lambda: True):
        file_act = b.to_action()

    assert isinstance(file_act, action.ActionList)
    assert len(file_act.actions) == 3
    backup_act = file_act.actions[0]
    copy_act = file_act.actions[1]
    chmod_act = file_act.actions[2]
    assert isinstance(backup_act, backup.FileBackupAction)
    assert isinstance(copy_act, copy.FileCopyAction)
    assert isinstance(chmod_act, modify.FileChmodAction)

    assert backup_act.src == '/p/q/r'
    assert backup_act.backup_dir == '/m/n'
    assert backup_act.logfile == '/m/n.log'
    assert copy_act.src == '/a/b/c'
    assert copy_act.dst == '/p/q/r'
    assert '{0:o}'.format(chmod_act.mode) == '600'
    assert chmod_act.target == copy_act.dst


@istest
def file_create_nouser():
    """
    File Block Create Without User Skips Chown
    Verifies that converting a file create block to an action when the
    user attribute is unset leaves out the chown.
    """
    b = src.block.file_block.FileBlock(dummy_context)
    b.set('action', 'create')
    b.set('target', '/p/q/r')
    b.set('group', 'nogroup')
    b.set('mode', '0600')

    # skip backup just to generate a simpler action
    with mock.patch('src.util.ugo.is_root', lambda: True), \
         mock.patch('os.path.exists', lambda f: False):
        file_act = b.to_action()

    assert isinstance(file_act, action.ActionList)
    assert len(file_act.actions) == 2
    touch = file_act.actions[0]
    chmod_act = file_act.actions[1]
    assert isinstance(touch, create.FileCreateAction)
    assert isinstance(chmod_act, modify.FileChmodAction)

    assert touch.dst == '/p/q/r'
    assert '{0:o}'.format(chmod_act.mode) == '600'
    assert chmod_act.target == '/p/q/r'


@istest
def file_copy_nogroup():
    """
    File Block Copy Without Group Skips Chown
    Verifies that converting a file copy block to an action when the
    group attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock(dummy_context)
    b.set('action', 'copy')
    b.set('source', '/a/b/c')
    b.set('target', '/p/q/r')
    b.set('user', 'user1')
    b.set('mode', '0600')

    # skip backup just to generate a simpler action
    with mock.patch('src.util.ugo.is_root', lambda: True), \
         mock.patch('os.path.exists', lambda f: False):
        file_act = b.to_action()

    assert isinstance(file_act, action.ActionList)
    assert len(file_act.actions) == 3
    backup_act = file_act.actions[0]
    copy_act = file_act.actions[1]
    chmod_act = file_act.actions[2]
    assert isinstance(backup_act, backup.FileBackupAction)
    assert isinstance(copy_act, copy.FileCopyAction)
    assert isinstance(chmod_act, modify.FileChmodAction)

    assert backup_act.src == '/p/q/r'
    assert backup_act.backup_dir == '/m/n'
    assert backup_act.logfile == '/m/n.log'
    assert copy_act.src == '/a/b/c'
    assert copy_act.dst == '/p/q/r'
    assert '{0:o}'.format(chmod_act.mode) == '600'
    assert chmod_act.target == copy_act.dst


@istest
def file_create_nogroup():
    """
    File Block Create Without Group Skips Chown
    Verifies that converting a file create block to an action when the
    group attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock(dummy_context)
    b.set('action', 'create')
    b.set('target', '/p/q/r')
    b.set('user', 'user1')
    b.set('mode', '0600')

    # skip backup just to generate a simpler action
    with mock.patch('src.util.ugo.is_root', lambda: True), \
         mock.patch('os.path.exists', lambda f: False):
        file_act = b.to_action()

    assert isinstance(file_act, action.ActionList)
    assert len(file_act.actions) == 2
    touch = file_act.actions[0]
    chmod_act = file_act.actions[1]
    assert isinstance(touch, create.FileCreateAction)
    assert isinstance(chmod_act, modify.FileChmodAction)

    assert touch.dst == '/p/q/r'
    assert '{0:o}'.format(chmod_act.mode) == '600'
    assert chmod_act.target == '/p/q/r'


@istest
def file_copy_nomode():
    """
    File Block Copy Without Mode Skips Chmod
    Verifies that converting a file copy block to an action when the
    mode attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock(dummy_context)
    b.set('action', 'copy')
    b.set('source', '/a/b/c')
    b.set('target', '/p/q/r')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    # skip chown, for simplicity
    with mock.patch('src.util.ugo.is_root', lambda: False):
        file_act = b.to_action()

    assert isinstance(file_act, action.ActionList)
    assert len(file_act.actions) == 3
    backup_act = file_act.actions[0]
    copy_act = file_act.actions[1]
    chown_act = file_act.actions[2]

    assert isinstance(backup_act, backup.FileBackupAction)
    assert isinstance(copy_act, copy.FileCopyAction)
    assert isinstance(chown_act, modify.FileChownAction)

    assert backup_act.src == '/p/q/r'
    assert backup_act.backup_dir == '/m/n'
    assert backup_act.logfile == '/m/n.log'
    assert copy_act.src == '/a/b/c'
    assert copy_act.dst == '/p/q/r'
    assert chown_act.user == 'user1'
    assert chown_act.group == 'nogroup'
    assert chown_act.target == copy_act.dst


@istest
def file_create_nomode():
    """
    File Block Create Without Mode Skips Chmod
    Verifies that converting a file create block to an action when the
    mode attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock(dummy_context)
    b.set('action', 'create')
    b.set('target', '/p/q/r')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    # skip chown and backup just to generate a simpler action
    with mock.patch('src.util.ugo.is_root', lambda: False), \
         mock.patch('os.path.exists', lambda f: False):
        act = b.to_action()

    assert isinstance(act, action.ActionList)
    assert len(act.actions) == 2
    touch = act.actions[0]
    chown = act.actions[1]
    assert isinstance(touch, create.FileCreateAction)
    assert isinstance(chown, modify.FileChownAction)

    assert touch.dst == '/p/q/r'
    assert chown.user == 'user1'
    assert chown.group == 'nogroup'
    assert chown.target == touch.dst


@istest
def file_copy_fails_nosource():
    """
    File Block Copy Fails Without Source
    Verifies that converting a file copy block to an action when the
    source attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock(dummy_context)
    b.set('action', 'copy')
    b.set('target', '/p/q/r')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    b.set('mode', '0600')
    ensure_except(BlockException, b.to_action)


@istest
def file_copy_fails_notarget():
    """
    File Block Copy Fails Without Target
    Verifies that converting a file copy block to an action when the
    target attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock(dummy_context)
    b.set('action', 'copy')
    b.set('source', '/a/b/c')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    b.set('mode', '0600')
    ensure_except(BlockException, b.to_action)


@istest
def file_create_fails_notarget():
    """
    File Block Create Fails Without Target
    Verifies that converting a file create block to an action when the
    target attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock(dummy_context)
    b.set('action', 'create')
    b.set('source', '/a/b/c')
    b.set('user', 'user1')
    b.set('group', 'nogroup')
    b.set('mode', '0600')
    ensure_except(BlockException, b.to_action)


@istest
def file_path_expand():
    """
    File Block Path Expand
    Tests the results of expanding relative paths in a File block.
    """
    b = src.block.file_block.FileBlock(dummy_context)
    b.set('source', 'p/q/r/s')
    b.set('target', 't/u/v/w/x/y/z/1/2/3/../3')
    root_dir = 'file/root/directory'
    b.expand_file_paths(root_dir)
    source_loc = os.path.join(root_dir, 'p/q/r/s')
    assert b.get('source') == source_loc
    target_loc = os.path.join(root_dir, 't/u/v/w/x/y/z/1/2/3/../3')
    assert b.get('target') == target_loc


@istest
def file_path_expand_fail_notarget():
    """
    File Block Path Expand Fails Without Target
    Verifies that a File Block with the target attribute unset raises
    a BlockException when paths are expanded.
    """
    b = src.block.file_block.FileBlock(dummy_context)
    b.set('action', 'create')
    b.set('source', 'p/q/r/s')
    b.set('user', 'user1')
    b.set('group', 'user1')
    b.set('mode', '644')
    root_dir = 'file/root/directory'
    ensure_except(BlockException, b.expand_file_paths, root_dir)
