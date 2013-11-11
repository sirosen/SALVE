#!/usr/bin/python

from nose.tools import istest
import mock

from lib.parse.tokenize import Token
import lib.execute.action as action
import lib.execute.block as block

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
def empty_manifest_to_action_error():
    try:
        b = block.ManifestBlock()
        al = b.to_action()
        assert False
    except KeyError:
        pass
    else:
        assert False

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
