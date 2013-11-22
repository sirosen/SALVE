#!/usr/bin/python

from nose.tools import istest
import os, mock

from tests.utils.exceptions import ensure_except
from src.block.base_block import BlockException

import src.execute.action as action
import src.block.file_block

@istest
def file_copy_to_action():
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    act = b.to_action()
    assert isinstance(act,action.ShellAction)
    assert act.cmds[0] == 'cp /a/b/c /p/q/r'
    assert 'chmod 0600 /p/q/r' in act.cmds
    assert 'chown user1:nogroup /p/q/r' not in act.cmds

@istest
def file_copy_chmod_as_root():
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    with mock.patch('os.geteuid',lambda:0):
        act = b.to_action()
        assert isinstance(act,action.ShellAction)
        assert act.cmds[0] == 'cp /a/b/c /p/q/r'
        assert 'chmod 0600 /p/q/r' in act.cmds
        assert 'chown user1:nogroup /p/q/r' in act.cmds

@istest
def file_create_to_action():
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    act = b.to_action()
    assert isinstance(act,action.ShellAction)
    assert act.cmds[0] == 'touch /p/q/r'
    assert 'chmod 0600 /p/q/r' in act.cmds
    assert 'chown user1:nogroup /p/q/r' not in act.cmds

@istest
def file_create_chmod_as_root():
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    with mock.patch('os.geteuid',lambda:0):
        act = b.to_action()
        assert isinstance(act,action.ShellAction)
        assert act.cmds[0] == 'touch /p/q/r'
        assert 'chmod 0600 /p/q/r' in act.cmds
        assert 'chown user1:nogroup /p/q/r' in act.cmds

@istest
def file_expandpaths_fails_notarget():
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    ensure_except(BlockException,b.expand_file_paths,'/')

@istest
def file_copy_fails_nosource():
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('target','/p/q/r')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    ensure_except(BlockException,b.to_action)

@istest
def file_copy_fails_notarget():
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    ensure_except(BlockException,b.to_action)

@istest
def file_create_fails_notarget():
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('source','/a/b/c')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    ensure_except(BlockException,b.to_action)

@istest
def file_copy_fails_nouser():
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('group','nogroup')
    b.set('mode','0600')
    ensure_except(BlockException,b.to_action)

@istest
def file_create_fails_nouser():
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('group','nogroup')
    b.set('mode','0600')
    ensure_except(BlockException,b.to_action)

@istest
def file_copy_fails_nomode():
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('user','user1')
    b.set('group','nogroup')
    ensure_except(BlockException,b.to_action)

@istest
def file_create_fails_nomode():
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('user','user1')
    b.set('group','nogroup')
    ensure_except(BlockException,b.to_action)

@istest
def file_copy_fails_nogroup():
    b = src.block.file_block.FileBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('user','user1')
    ensure_except(BlockException,b.to_action)

@istest
def file_create_fails_nogroup():
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('user','user1')
    ensure_except(BlockException,b.to_action)

@istest
def file_path_expand():
    f = src.block.file_block.FileBlock()
    f.set('source','p/q/r/s')
    f.set('target','t/u/v/w/x/y/z/1/2/3/../3')
    root_dir = 'file/root/directory'
    f.expand_file_paths(root_dir)
    source_loc = os.path.join(root_dir,'p/q/r/s')
    assert f.get('source') == source_loc
    target_loc = os.path.join(root_dir,'t/u/v/w/x/y/z/1/2/3/../3')
    assert f.get('target') == target_loc

@istest
def file_path_expand_fail_notarget():
    b = src.block.directory_block.DirBlock()
    b.set('action','create')
    b.set('source','p/q/r/s')
    b.set('user','user1')
    b.set('group','user1')
    b.set('mode','644')
    root_dir = 'file/root/directory'
    ensure_except(BlockException,b.expand_file_paths,root_dir)
