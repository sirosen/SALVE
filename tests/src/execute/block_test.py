#!/usr/bin/python

from nose.tools import istest
import os
import mock

from src.reader.tokenize import Token
import src.execute.action as action
import src.execute.block as block
import src.settings.config


_testfile_dir = os.path.join(os.path.dirname(__file__),'files')
def get_full_path(filename):
    return os.path.join(_testfile_dir,filename)

def mock_expanduser(string):
    user = os.environ['USER']
    string = string.replace('~'+user,_testfile_dir)
    if string[0] == '~':
        string = _testfile_dir+string[1:]
    return string

_dummy_conf = None
with mock.patch('os.path.expanduser',mock_expanduser):
    _dummy_conf = src.settings.config.SALVEConfig()

@istest
def block_is_abstract():
    try:
        block.Block()
        assert False
    except TypeError:
        pass
    else:
        assert False

@istest
def invalid_block_id():
    invalid_id = Token('invalid_block_id',Token.types.IDENTIFIER)
    try:
        block.block_from_identifier(invalid_id)
        assert False
    except ValueError:
        pass
    else:
        assert False

@istest
def valid_file_id():
    file_id = Token('file',Token.types.IDENTIFIER)
    file_block = block.block_from_identifier(file_id)
    assert isinstance(file_block,block.FileBlock)

@istest
def valid_manifest_id():
    manifest_id = Token('manifest',Token.types.IDENTIFIER)
    manifest_block = block.block_from_identifier(manifest_id)
    assert isinstance(manifest_block,block.ManifestBlock)

@istest
def sourceless_manifest_to_action_error():
    try:
        b = block.ManifestBlock()
        al = b.to_action()
        assert False
    except AssertionError: pass
    else: assert False

@istest
def file_block_create_to_action():
    b = block.FileBlock()
    b.attrs = {'action':'create',
               'source':'/a/b/c',
               'target':'/p/q/r',
               'user':'user1',
               'group':'nogroup',
               'mode':'0600'}
    act = b.to_action()
    assert isinstance(act,action.ShellAction)
    assert act.cmds[0] == 'cp /a/b/c /p/q/r'
    assert 'chown user1:nogroup /p/q/r' in act.cmds
    assert 'chmod 0600 /p/q/r' in act.cmds

@istest
def sourceless_manifest_expand_error():
    try:
        b = block.ManifestBlock()
        b.expand_blocks(_dummy_conf)
        assert False
    except AssertionError: pass
    else: assert False

@istest
def empty_manifest_expand():
    b = block.ManifestBlock(source=get_full_path('valid1.manifest'))
    b.expand_blocks(_dummy_conf)
    assert len(b.sub_blocks) == 0

@istest
def recursive_manifest_error():
    b = block.ManifestBlock(source=get_full_path('invalid1.manifest'))
    try:
        b.expand_blocks(_dummy_conf)
        assert False
    except block.BlockException: pass
    else: assert False
