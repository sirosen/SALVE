#!/usr/bin/python

from nose.tools import istest
import os, mock

from tests.utils.exceptions import ensure_except
from src.block.base_block import BlockException

import src.execute.action as action
import src.execute.backup as backup
import src.block.file_block

@istest
def file_copy_to_action():
    """
    File Block Copy To Action
    Verifies the result of converting a file copy block to an action.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    with mock.patch('os.path.exists', lambda f: True):
        act = b.to_action()

    assert isinstance(act,action.ActionList)
    assert len(act.actions) == 2
    backup_act = act.actions[0]
    shell_act = act.actions[1]
    assert isinstance(backup_act,backup.FileBackupAction)
    assert isinstance(shell_act,action.ShellAction)

    assert shell_act.cmds[0] == 'cp /a/b/c /p/q/r'
    assert 'chmod 0600 /p/q/r' in shell_act.cmds
    assert 'chown user1:nogroup /p/q/r' not in shell_act.cmds

@istest
def file_copy_to_action_nobackup():
    """
    File Block Copy To Action (No Backup)
    Verifies the result of converting a file copy block to an action
    when the target does not exist.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    with mock.patch('os.path.exists', lambda f: False):
        shell_act = b.to_action()

    assert isinstance(shell_act,action.ShellAction)
    assert shell_act.cmds[0] == 'cp /a/b/c /p/q/r'
    assert 'chmod 0600 /p/q/r' in shell_act.cmds
    assert 'chown user1:nogroup /p/q/r' not in shell_act.cmds

@istest
def file_copy_chmod_as_root():
    """
    File Block Copy To Action (As Root)
    Verifies the result of converting a file copy block to an action
    when the EUID is 0.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    with mock.patch('os.geteuid',lambda:0):
        with mock.patch('os.path.exists', lambda f: True):
            act = b.to_action()

    assert isinstance(act,action.ActionList)
    assert len(act.actions) == 2
    backup_act = act.actions[0]
    shell_act = act.actions[1]
    assert isinstance(backup_act,backup.FileBackupAction)
    assert isinstance(shell_act,action.ShellAction)

    assert shell_act.cmds[0] == 'cp /a/b/c /p/q/r'
    assert 'chmod 0600 /p/q/r' in shell_act.cmds
    assert 'chown user1:nogroup /p/q/r' in shell_act.cmds

@istest
def file_create_to_action():
    """
    File Block Create To Action
    Verifies the result of converting a file create block to an action.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    with mock.patch('os.path.exists', lambda f: True):
        act = b.to_action()

    assert isinstance(act,action.ActionList)
    assert len(act.actions) == 2
    backup_act = act.actions[0]
    shell_act = act.actions[1]
    assert isinstance(backup_act,backup.FileBackupAction)
    assert isinstance(shell_act,action.ShellAction)

    assert shell_act.cmds[0] == 'touch /p/q/r'
    assert 'chmod 0600 /p/q/r' in shell_act.cmds
    assert 'chown user1:nogroup /p/q/r' not in shell_act.cmds

@istest
def file_create_to_action_nobackup():
    """
    File Block Create To Action (No Backup)
    Verifies the result of converting a file create block to an action
    when the target does not exist.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    with mock.patch('os.path.exists', lambda f: False):
        shell_act = b.to_action()

    assert isinstance(shell_act,action.ShellAction)

    assert shell_act.cmds[0] == 'touch /p/q/r'
    assert 'chmod 0600 /p/q/r' in shell_act.cmds
    assert 'chown user1:nogroup /p/q/r' not in shell_act.cmds

@istest
def file_create_chmod_as_root():
    """
    File Block Create To Action (As Root)
    Verifies the result of converting a file create block to an action
    when the EUID is 0.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    with mock.patch('os.geteuid',lambda:0):
        with mock.patch('os.path.exists', lambda f: True):
            act = b.to_action()

    assert isinstance(act,action.ActionList)
    assert len(act.actions) == 2
    backup_act = act.actions[0]
    shell_act = act.actions[1]
    assert isinstance(backup_act,backup.FileBackupAction)
    assert isinstance(shell_act,action.ShellAction)

    assert shell_act.cmds[0] == 'touch /p/q/r'
    assert 'chmod 0600 /p/q/r' in shell_act.cmds
    assert 'chown user1:nogroup /p/q/r' in shell_act.cmds

@istest
def file_copy_fails_nosource():
    """
    File Block Copy Fails Without Source
    Verifies that converting a file copy block to an action when the
    source attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    ensure_except(BlockException,b.to_action)

@istest
def file_copy_fails_notarget():
    """
    File Block Copy Fails Without Target
    Verifies that converting a file copy block to an action when the
    target attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    ensure_except(BlockException,b.to_action)

@istest
def file_create_fails_notarget():
    """
    File Block Create Fails Without Target
    Verifies that converting a file create block to an action when the
    target attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('source','/a/b/c')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    ensure_except(BlockException,b.to_action)

@istest
def file_copy_fails_nouser():
    """
    File Block Copy Fails Without User
    Verifies that converting a file copy block to an action when the
    user attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('group','nogroup')
    b.set('mode','0600')
    ensure_except(BlockException,b.to_action)

@istest
def file_create_fails_nouser():
    """
    File Block Create Fails Without User
    Verifies that converting a file create block to an action when the
    user attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('group','nogroup')
    b.set('mode','0600')
    ensure_except(BlockException,b.to_action)

@istest
def file_copy_fails_nomode():
    """
    File Block Copy Fails Without Mode
    Verifies that converting a file copy block to an action when the
    mode attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    ensure_except(BlockException,b.to_action)

@istest
def file_create_fails_nomode():
    """
    File Block Create Fails Without Mode
    Verifies that converting a file create block to an action when the
    mode attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    ensure_except(BlockException,b.to_action)

@istest
def file_copy_fails_nogroup():
    """
    File Block Copy Fails Without Group
    Verifies that converting a file copy block to an action when the
    group attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    ensure_except(BlockException,b.to_action)

@istest
def file_create_fails_nogroup():
    """
    File Block Create Fails Without Group
    Verifies that converting a file create block to an action when the
    group attribute is unset raises a BlockException.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    ensure_except(BlockException,b.to_action)

@istest
def file_path_expand():
    """
    File Block Path Expand
    Tests the results of expanding relative paths in a File block.
    """
    b = src.block.file_block.FileBlock()
    b.set('source','p/q/r/s')
    b.set('target','t/u/v/w/x/y/z/1/2/3/../3')
    b.set('backup_dir','m/n')
    b.set('backup_log','m/n.log')
    root_dir = 'file/root/directory'
    b.expand_file_paths(root_dir)
    source_loc = os.path.join(root_dir,'p/q/r/s')
    assert b.get('source') == source_loc
    target_loc = os.path.join(root_dir,'t/u/v/w/x/y/z/1/2/3/../3')
    assert b.get('target') == target_loc
    backup_dir_loc = os.path.join(root_dir,'m/n')
    assert b.get('backup_dir') == backup_dir_loc
    backup_log_loc = os.path.join(root_dir,'m/n.log')
    assert b.get('backup_log') == backup_log_loc

@istest
def file_path_expand_fail_notarget():
    """
    File Block Path Expand Fails Without Target
    Verifies that a File Block with the target attribute unset raises
    a BlockException when paths are expanded.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('source','p/q/r/s')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','user1')
    b.set('mode','644')
    root_dir = 'file/root/directory'
    ensure_except(BlockException,b.expand_file_paths,root_dir)

@istest
def file_path_expand_fail_nobackupdir():
    """
    File Block Path Expand Fails Without Backup Dir
    Verifies that a File Block with the backup_dir attribute unset
    raises a BlockException when paths are expanded.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('source','p/q/r/s')
    b.set('target','t/u/v')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','user1')
    b.set('mode','644')
    root_dir = 'file/root/directory'
    ensure_except(BlockException,b.expand_file_paths,root_dir)

@istest
def file_path_expand_fail_nobackuplog():
    """
    File Block Path Expand Fails Without Backup Log
    Verifies that a File Block with the backup_log attribute unset
    raises a BlockException when paths are expanded.
    """
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('source','p/q/r/s')
    b.set('target','t/u/v')
    b.set('backup_dir','/m/n')
    b.set('user','user1')
    b.set('group','user1')
    b.set('mode','644')
    root_dir = 'file/root/directory'
    ensure_except(BlockException,b.expand_file_paths,root_dir)
