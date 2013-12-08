#!/usr/bin/python

from nose.tools import istest
import os, mock

from tests.utils.exceptions import ensure_except
from src.block.base import BlockException

import src.execute.action as action
import src.execute.backup as backup
import src.block.directory_block

@istest
def dir_create_to_action():
    """
    Directory Block Create To Action
    Verifies the result of converting a Dir Block to an Action.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','755')

    with mock.patch('os.path.exists',lambda f: True):
        mkdir = b.to_action()

    assert isinstance(mkdir,action.ShellAction)

    assert mkdir.cmd == 'mkdir -p -m 755 /p/q/r'

@istest
def dir_create_chmod_as_root():
    """
    Directory Block Create To Action (As Root)
    Verifies the result of converting a Dir Block to an Action.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','755')
    with mock.patch('os.geteuid',lambda:0):
        with mock.patch('os.path.exists',lambda f: True):
            dir_act = b.to_action()

    assert isinstance(dir_act,action.ActionList)
    assert len(dir_act.actions) == 2
    mkdir = dir_act.actions[0]
    chown = dir_act.actions[1]

    assert mkdir.cmd == 'mkdir -p -m 755 /p/q/r'
    assert chown.cmd == 'chown user1:nogroup /p/q/r'

@istest
def empty_dir_copy_to_action():
    """
    Directory Block Copy To Action (Empty Dir)
    Verifies the result of converting a Dir Block to an Action.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','744')
    with mock.patch('os.path.exists',lambda f: True):
        with mock.patch('os.walk',lambda d: []):
            dir_act = b.to_action()

    assert isinstance(dir_act,action.ActionList)
    assert len(dir_act.actions) == 1
    mkdir_act = dir_act.actions[0]

    assert mkdir_act.cmd == 'mkdir -p -m 744 /p/q/r'

@istest
def dir_copy_chmod_as_root():
    """
    Directory Block Copy To Action (As Root)
    Verifies the result of converting a Dir Block to an Action.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','744')
    with mock.patch('os.geteuid',lambda:0):
        with mock.patch('os.path.exists',lambda f: True):
            with mock.patch('os.walk',lambda d: []):
                al = b.to_action()

    assert isinstance(al,action.ActionList)
    assert len(al.actions) == 2
    mkdir_act = al.actions[0]
    chown_act = al.actions[1]

    assert isinstance(mkdir_act,action.ShellAction)
    assert isinstance(chown_act,action.ShellAction)

    assert mkdir_act.cmd == 'mkdir -p -m 744 /p/q/r'
    assert chown_act.cmd == 'chown -R user1:nogroup /p/q/r', "%s" % chown_act.cmd

@istest
def dir_copy_fails_nosource():
    """
    Directory Block Copy Fails Without Source
    Verifies that converting a Dir Block to an Action raises a
    BlockException.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','copy')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','755')
    ensure_except(BlockException,b.to_action)

@istest
def dir_copy_fails_notarget():
    """
    Directory Block Copy Fails Without Target
    Verifies that converting a Dir Block to an Action raises a
    BlockException.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','755')
    ensure_except(BlockException,b.to_action)

@istest
def dir_create_fails_notarget():
    """
    Directory Block Create Fails Without Target
    Verifies that converting a Dir Block to an Action raises a
    BlockException.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','create')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','755')
    ensure_except(BlockException,b.to_action)

@istest
def dir_copy_fails_nouser():
    """
    Directory Block Copy Fails Without User
    Verifies that converting a Dir Block to an Action raises a
    BlockException.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('group','nogroup')
    b.set('mode','755')
    ensure_except(BlockException,b.to_action)

@istest
def dir_create_fails_nouser():
    """
    Directory Block Create Fails Without User
    Verifies that converting a Dir Block to an Action raises a
    BlockException.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('group','nogroup')
    b.set('mode','755')
    ensure_except(BlockException,b.to_action)

@istest
def dir_copy_fails_nomode():
    """
    Directory Block Copy Fails Without Mode
    Verifies that converting a Dir Block to an Action raises a
    BlockException.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    ensure_except(BlockException,b.to_action)

@istest
def dir_create_fails_nomode():
    """
    Directory Block Create Fails Without Mode
    Verifies that converting a Dir Block to an Action raises a
    BlockException.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    ensure_except(BlockException,b.to_action)

@istest
def dir_copy_fails_nogroup():
    """
    Directory Block Copy Fails Without Group
    Verifies that converting a Dir Block to an Action raises a
    BlockException.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('mode','755')
    ensure_except(BlockException,b.to_action)

@istest
def dir_create_fails_nogroup():
    """
    Directory Block Create Fails Without Group
    Verifies that converting a Dir Block to an Action raises a
    BlockException.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('mode','755')
    ensure_except(BlockException,b.to_action)

@istest
def dir_path_expand():
    """
    Directory Block Path Expand
    Verifies the results of path expansion in a Dir block.
    """
    b = src.block.directory_block.DirBlock()
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
    backup_loc = os.path.join(root_dir,'m/n')
    assert b.get('backup_dir') == backup_loc
    backup_log_loc = os.path.join(root_dir,'m/n.log')
    assert b.get('backup_log') == backup_log_loc

@istest
def dir_path_expand_fail_notarget():
    """
    Directory Block Path Expand Fails Without Target
    Verifies that path expansion fails when there is no "target"
    attribute.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','create')
    b.set('user','user1')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('group','user1')
    b.set('mode','755')
    root_dir = 'file/root/directory'
    ensure_except(BlockException,b.expand_file_paths,root_dir)

@istest
def dir_path_expand_fail_nobackupdir():
    """
    Directory Block Path Expand Fails Without Backup Dir
    Verifies that path expansion fails when there is no "backup_dir"
    attribute.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','create')
    b.set('user','user1')
    b.set('target','t/u/v/w/x/y/z/1/2/3/../3')
    b.set('backup_log','/m/n.log')
    b.set('group','user1')
    b.set('mode','755')
    root_dir = 'file/root/directory'
    ensure_except(BlockException,b.expand_file_paths,root_dir)

@istest
def dir_path_expand_fail_nobackuplog():
    """
    Directory Block Path Expand Fails Without Backup Log
    Verifies that path expansion fails when there is no "backup_log"
    attribute.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','create')
    b.set('user','user1')
    b.set('target','t/u/v/w/x/y/z/1/2/3/../3')
    b.set('backup_dir','/m/n')
    b.set('group','user1')
    b.set('mode','755')
    root_dir = 'file/root/directory'
    ensure_except(BlockException,b.expand_file_paths,root_dir)

@istest
def dir_to_action_fail_noaction():
    """
    Directory Block To Action Fails Without Action
    Verifies that block to action conversion fails when there is no
    "action" attribute.
    """
    b = src.block.directory_block.DirBlock()
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','755')
    ensure_except(BlockException,b.to_action)

@istest
def dir_to_action_fail_unknown_action():
    """
    Directory Block To Action Fails Unknown Action
    Verifies that block to action conversion fails when the "action"
    attribute has an unrecognized value.
    """
    b = src.block.directory_block.DirBlock()
    b.set('action','UNDEFINED_ACTION')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('backup_dir','/m/n')
    b.set('backup_log','/m/n.log')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','755')
    ensure_except(BlockException,b.to_action)
