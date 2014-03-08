#!/usr/bin/python

import os
import mock
from nose.tools import istest
from tests.utils.exceptions import ensure_except

import src.execute.action
import src.execute.backup
import src.execute.copy
import src.block.manifest_block
import src.block.base
import src.util.locations as locations

from tests.unit.block.block_test import _dummy_conf, get_full_path
from src.util.context import SALVEContext, ExecutionContext

@istest
def sourceless_manifest_to_action_error():
    """
    Manifest Block To Action Fails Without Action
    Verifies that a Manifest block raises a BlockException when
    converted to an action if the action attribute is unspecified.
    """
    ctx = SALVEContext(exec_context=ExecutionContext())
    b = src.block.manifest_block.ManifestBlock(ctx)
    ensure_except(src.block.base.BlockException,b.to_action)

@istest
def sourceless_manifest_expand_error():
    """
    Manifest Block Path Expand Fails Without Source
    Verifies that a Manifest block raises a BlockException when paths
    are expanded if the source attribute is unspecified.
    """
    ctx = SALVEContext(exec_context=ExecutionContext())
    b = src.block.manifest_block.ManifestBlock(ctx)
    ensure_except(src.block.base.BlockException,
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
    ctx = SALVEContext(exec_context=ExecutionContext())
    b = src.block.manifest_block.ManifestBlock(ctx,
        source=get_full_path('valid1.manifest'))
    b.expand_blocks(locations.get_salve_root(),_dummy_conf)
    assert len(b.sub_blocks) == 0

@istest
def recursive_manifest_error():
    """
    Manifest Block Self-Inclusion Error
    Verifies that a Manifest block which includes itself raises a
    BlockException when expanded.
    """
    ctx = SALVEContext(exec_context=ExecutionContext())
    b = src.block.manifest_block.ManifestBlock(ctx,
        source=get_full_path('invalid1.manifest'))
    ensure_except(src.block.base.BlockException,
                  b.expand_blocks,
                  locations.get_salve_root(),
                  _dummy_conf)

@istest
def sub_block_expand():
    """
    Manifest Block SubBlock Expand
    Verifies that Manifest block expansion works normally.
    """
    ctx = SALVEContext(exec_context=ExecutionContext())
    b = src.block.manifest_block.ManifestBlock(ctx,
        source=get_full_path('valid2.manifest'))
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
    dummy_exec_context = ExecutionContext()
    dummy_exec_context.set('backup_dir','/m/n')
    dummy_exec_context.set('backup_log','/m/n.log')
    dummy_context = SALVEContext(exec_context=dummy_exec_context)
    b = src.block.manifest_block.ManifestBlock(dummy_context,
        source=get_full_path('valid2.manifest'))
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
        with mock.patch('os.access', lambda f,p: True):
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
                      src.execute.copy.FileCopyAction)
