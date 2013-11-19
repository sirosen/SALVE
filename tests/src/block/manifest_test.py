#!/usr/bin/python

from nose.tools import istest
import os, mock
from tests.utils.exceptions import ensure_except

import src.execute.action
import src.block.manifest_block
import src.block.base_block
import src.util.locations as locations

from tests.src.block.block_test import _dummy_conf, get_full_path

@istest
def sourceless_manifest_to_action_error():
    b = src.block.manifest_block.ManifestBlock()
    ensure_except(src.block.base_block.BlockException,b.to_action)

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

@istest
def sub_block_to_action():
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
    act = b.to_action()
    assert isinstance(act,src.execute.action.ActionList)
    assert len(act.actions) == 2
    assert isinstance(act.actions[0],src.execute.action.ActionList)
    assert len(act.actions[0].actions) == 0
    assert isinstance(act.actions[1],src.execute.action.ShellAction)
