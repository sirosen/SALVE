#!/usr/bin/python

import os
import mock
from nose.tools import istest
from tests.utils.exceptions import ensure_except

import salve.execute.action
import salve.execute.backup
import salve.execute.copy
import salve.block.manifest_block
import salve.block.base
import salve.util.locations as locations

from tests.unit.block import get_full_path
from tests.unit.block import dummy_file_context, dummy_exec_context
from tests.unit.block import dummy_conf, dummy_logger


@istest
def sourceless_manifest_compile_error():
    """
    Unit: Manifest Compilation Fails Without Action
    Verifies that a Manifest block raises a BlockException when
    compiled if the action attribute is unspecified.
    """
    with mock.patch('salve.logger', dummy_logger):
        b = salve.block.manifest_block.ManifestBlock(dummy_file_context)
        ensure_except(salve.block.base.BlockException, b.compile)


@istest
def sourceless_manifest_expand_error():
    """
    Unit: Manifest Block Path Expand Fails Without Source
    Verifies that a Manifest block raises a BlockException when paths
    are expanded if the source attribute is unspecified.
    """
    with mock.patch('salve.logger', dummy_logger):
        b = salve.block.manifest_block.ManifestBlock(dummy_file_context)
        ensure_except(salve.block.base.BlockException,
                      b.expand_blocks,
                      locations.get_salve_root(),
                      dummy_conf)


@istest
def empty_manifest_expand():
    """
    Unit: Manifest Block SubBlock Expand Empty List
    Verifies that a Manifest block with no sub-blocks expands without
    errors.
    """
    with mock.patch('salve.logger', dummy_logger):
        b = salve.block.manifest_block.ManifestBlock(dummy_file_context,
            source=get_full_path('valid1.manifest'))
        b.expand_blocks(locations.get_salve_root(), dummy_conf)
    assert len(b.sub_blocks) == 0


@istest
def recursive_manifest_error():
    """
    Unit: Manifest Block Self-Inclusion Error
    Verifies that a Manifest block which includes itself raises a
    BlockException when expanded.
    """
    with mock.patch('salve.logger', dummy_logger):
        b = salve.block.manifest_block.ManifestBlock(dummy_file_context,
            source=get_full_path('invalid1.manifest'))
        ensure_except(salve.block.base.BlockException,
                      b.expand_blocks,
                      locations.get_salve_root(),
                      dummy_conf)


@istest
def sub_block_expand():
    """
    Unit: Manifest Block SubBlock Expand
    Verifies that Manifest block expansion works normally.
    """
    with mock.patch('salve.logger', dummy_logger):
        b = salve.block.manifest_block.ManifestBlock(dummy_file_context,
            source=get_full_path('valid2.manifest'))
        b.expand_blocks(locations.get_salve_root(), dummy_conf)
    assert len(b.sub_blocks) == 2
    man_block = b.sub_blocks[0]
    file_block = b.sub_blocks[1]
    assert isinstance(man_block, salve.block.manifest_block.ManifestBlock)
    assert isinstance(file_block, salve.block.file_block.FileBlock)
    assert man_block.get('source') == get_full_path('valid1.manifest')
    assert file_block.get('source') == get_full_path('valid1.manifest')
    target_loc = os.path.join(locations.get_salve_root(), 'a/b/c')
    assert file_block.get('target') == target_loc


@istest
def sub_block_compile():
    """
    Unit: Manifest Block SubBlock Compile
    Verifies that Manifest block expansion followed by action
    conversion works normally.
    """
    with mock.patch('salve.logger', dummy_logger):
        b = salve.block.manifest_block.ManifestBlock(dummy_file_context,
            source=get_full_path('valid2.manifest'))
        b.expand_blocks(locations.get_salve_root(), dummy_conf)
    assert len(b.sub_blocks) == 2
    man_block = b.sub_blocks[0]
    file_block = b.sub_blocks[1]
    assert isinstance(man_block, salve.block.manifest_block.ManifestBlock)
    assert isinstance(file_block, salve.block.file_block.FileBlock)
    assert man_block.get('source') == get_full_path('valid1.manifest')
    assert file_block.get('source') == get_full_path('valid1.manifest')
    target_loc = os.path.join(locations.get_salve_root(), 'a/b/c')
    assert file_block.get('target') == target_loc

    with mock.patch('salve.logger', dummy_logger):
        with mock.patch('salve.exec_context', dummy_exec_context):
            with mock.patch('os.path.exists', lambda f: True):
                with mock.patch('os.access', lambda f, p: True):
                    act = b.compile()

    assert isinstance(act, salve.execute.action.ActionList)
    assert len(act.actions) == 2
    assert isinstance(act.actions[0], salve.execute.action.ActionList)
    assert len(act.actions[0].actions) == 0
    file_act = act.actions[1]
    assert isinstance(file_act, salve.execute.action.ActionList)
    assert isinstance(file_act.actions[0],
                      salve.execute.backup.FileBackupAction)
    assert isinstance(file_act.actions[1],
                      salve.execute.copy.FileCopyAction)
