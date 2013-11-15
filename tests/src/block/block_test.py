#!/usr/bin/python

from nose.tools import istest
import os
import mock

from tests.utils.exceptions import ensure_except

from src.reader.tokenize import Token
import src.execute.action as action
import src.block.base_block
import src.block.identifier
import src.block.manifest_block
import src.util.locations as locations
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
    ensure_except(TypeError,src.block.base_block.Block)

@istest
def invalid_block_id():
    invalid_id = Token('invalid_block_id',Token.types.IDENTIFIER)
    ensure_except(ValueError,
                  src.block.identifier.block_from_identifier,
                  invalid_id)

@istest
def valid_file_id():
    file_id = Token('file',Token.types.IDENTIFIER)
    file_block = src.block.identifier.block_from_identifier(file_id)
    assert isinstance(file_block,src.block.file_block.FileBlock)

@istest
def valid_manifest_id():
    manifest_id = Token('manifest',Token.types.IDENTIFIER)
    manifest_block = src.block.identifier.block_from_identifier(manifest_id)
    assert isinstance(manifest_block,src.block.manifest_block.ManifestBlock)

@istest
def sourceless_manifest_to_action_error():
    b = src.block.manifest_block.ManifestBlock()
    ensure_except(src.block.base_block.BlockException,b.to_action)

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
def sourceless_manifest_expand_error():
    b = src.block.manifest_block.ManifestBlock()
    ensure_except(src.block.base_block.BlockException,
                  b.expand_blocks,
                  locations.get_salve_root(),
                  _dummy_conf)

@istest
def empty_manifest_expand():
    b = src.block.manifest_block.ManifestBlock(source=get_full_path('valid1.manifest'))
    b.expand_blocks(locations.get_salve_root(),_dummy_conf)
    assert len(b.sub_blocks) == 0

@istest
def recursive_manifest_error():
    b = src.block.manifest_block.ManifestBlock(source=get_full_path('invalid1.manifest'))
    ensure_except(src.block.base_block.BlockException,
                  b.expand_blocks,
                  locations.get_salve_root(),
                  _dummy_conf)

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
def sub_block_expand():
    b = src.block.manifest_block.ManifestBlock(source=get_full_path('valid2.manifest'))
    b.expand_blocks(locations.get_salve_root(),_dummy_conf)
    assert len(b.sub_blocks) == 2
    man_block = b.sub_blocks[0]
    file_block = b.sub_blocks[1]
    assert isinstance(man_block,src.block.manifest_block.ManifestBlock)
    assert isinstance(file_block,src.block.file_block.FileBlock)
    assert man_block.get('source') == get_full_path('valid1.manifest')
    assert file_block.get('source') == get_full_path('valid1.manifest')
    target_loc = os.path.join(locations.get_salve_root(),'a/b/c')
    assert file_block.get('target') == target_loc
