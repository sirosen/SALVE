#!/usr/bin/python

from nose.tools import istest
import os

import src.execute.action as action
import src.block.directory_block

@istest
def dir_block_create_to_action():
    b = src.block.directory_block.DirBlock()
    b.set('action','create')
    b.set('target','/p/q/r')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    act = b.to_action()
    assert isinstance(act,action.ShellAction)
    assert act.cmds[0] == 'mkdir -p -m 0600 /p/q/r'
    assert act.cmds[1] == 'chown user1:nogroup /p/q/r'

@istest
def dir_block_copy_to_action():
    b = src.block.directory_block.DirBlock()
    b.set('action','copy')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0644')
    act = b.to_action()
    assert isinstance(act,action.ShellAction)
    assert act.cmds[0] == 'mkdir -p -m 0644 /p/q/r'
    assert act.cmds[1] == 'cp -r /a/b/c /p/q/r'
    assert act.cmds[2] == 'chown -R user1:nogroup /p/q/r'

@istest
def dir_path_expand():
    b = src.block.directory_block.DirBlock()
    b.set('source','p/q/r/s')
    b.set('target','t/u/v/w/x/y/z/1/2/3/../3')
    root_dir = 'file/root/directory'
    b.expand_file_paths(root_dir)
    source_loc = os.path.join(root_dir,'p/q/r/s')
    assert b.get('source') == source_loc
    target_loc = os.path.join(root_dir,'t/u/v/w/x/y/z/1/2/3/../3')
    assert b.get('target') == target_loc
