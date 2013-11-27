#!/usr/bin/python

from nose.tools import istest
import os, mock
from tests.utils.exceptions import ensure_except

import src.execute.action
import src.execute.backup
import src.block.manifest_block
import src.block.base_block
import src.util.locations as locations

from tests.src.block.block_test import _dummy_conf, get_full_path

@istest
def sourceless_manifest_to_action_error():
    """
    Manifest Block To Action Fails Without Action
    Verifies that a Manifest block raises a BlockException when
    converted to an action if the action attribute is unspecified.
    """
    b = src.block.manifest_block.ManifestBlock()
    ensure_except(src.block.base_block.BlockException,b.to_action)

@istest
def sourceless_manifest_expand_error():
    """
    Manifest Block Path Expand Fails Without Source
    Verifies that a Manifest block raises a BlockException when paths
    are expanded if the source attribute is unspecified.
    """
    b = src.block.manifest_block.ManifestBlock()
    ensure_except(src.block.base_block.BlockException,
                  b.expand_blocks,
                  locations.get_salve_root(),
                  _dummy_conf)

@istest
def empty_manifest_expand():
    """
    Manifest Block SubBlock Expand Empty List
    Verifies that a Manifest block with no sub-blocks expands without
    errors.
    """
    b = src.block.manifest_block.ManifestBlock(source=get_full_path('valid1.manifest'))
    b.expand_blocks(locations.get_salve_root(),_dummy_conf)
    assert len(b.sub_blocks) == 0

@istest
def recursive_manifest_error():
    """
    Manifest Block Self-Inclusion Error
    Verifies that a Manifest block which includes itself raises a
    BlockException when expanded.
    """
    b = src.block.manifest_block.ManifestBlock(source=get_full_path('invalid1.manifest'))
    ensure_except(src.block.base_block.BlockException,
                  b.expand_blocks,
                  locations.get_salve_root(),
                  _dummy_conf)

@istest
def sub_block_expand():
    """
    Manifest Block SubBlock Expand
    Verifies that Manifest block expansion works normally.
    """
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
    """
    Manifest Block SubBlock To Action
    Verifies that Manifest block expansion followed by action
    conversion works normally.
    """
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
    with mock.patch('os.path.exists', lambda f: True):
        act = b.to_action()
    assert isinstance(act,src.execute.action.ActionList)
    assert len(act.actions) == 2
    assert isinstance(act.actions[0],src.execute.action.ActionList)
    assert len(act.actions[0].actions) == 0
    file_act = act.actions[1]
    assert isinstance(file_act,src.execute.action.ActionList)
    assert isinstance(file_act.actions[0],
                      src.execute.backup.FileBackupAction)
    assert isinstance(file_act.actions[1],
                      src.execute.action.ShellAction)
