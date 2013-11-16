#!/usr/bin/python

from nose.tools import istest
import os

import src.execute.action as action
import src.block.file_block

@istest
def file_block_create_to_action():
    b = src.block.file_block.FileBlock()
    b.set('action','create')
    b.set('source','/a/b/c')
    b.set('target','/p/q/r')
    b.set('user','user1')
    b.set('group','nogroup')
    b.set('mode','0600')
    act = b.to_action()
    assert isinstance(act,action.ShellAction)
    assert act.cmds[0] == 'cp /a/b/c /p/q/r'
    assert 'chown user1:nogroup /p/q/r' in act.cmds
    assert 'chmod 0600 /p/q/r' in act.cmds

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
