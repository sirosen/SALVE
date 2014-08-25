#!/usr/bin/python

import os
import mock
from nose.tools import istest
from tests.util import ensure_except, full_path

from salve import action, block, paths
from salve.action import backup, copy

from salve.block import manifest_block, file_block

from tests.unit.block import dummy_file_context, dummy_exec_context, \
        dummy_conf, dummy_logger


@istest
def sourceless_manifest_compile_error():
    """
    Unit: Manifest Compilation Fails Without Action
    Verifies that a Manifest block raises a BlockException when
    compiled if the action attribute is unspecified.
    """
    with mock.patch('salve.logger', dummy_logger):
        b = manifest_block.ManifestBlock(dummy_file_context)
        ensure_except(block.BlockException, b.compile)


@istest
def sourceless_manifest_expand_error():
    """
    Unit: Manifest Block Path Expand Fails Without Source
    Verifies that a Manifest block raises a BlockException when paths
    are expanded if the source attribute is unspecified.
    """
    with mock.patch('salve.logger', dummy_logger):
        b = manifest_block.ManifestBlock(dummy_file_context)
        ensure_except(block.BlockException,
                      b.expand_blocks, '/',
                      dummy_conf)


@istest
def empty_manifest_expand():
    """
    Unit: Manifest Block SubBlock Expand Empty List
    Verifies that a Manifest block with no sub-blocks expands without
    errors.
    """
    with mock.patch('salve.logger', dummy_logger):
        b = manifest_block.ManifestBlock(dummy_file_context,
            source=full_path('empty.manifest'))
        b.expand_blocks('/', dummy_conf)
    assert len(b.sub_blocks) == 0


@istest
def recursive_manifest_error():
    """
    Unit: Manifest Block Self-Inclusion Error
    Verifies that a Manifest block which includes itself raises a
    BlockException when expanded.
    """
    invalid1_path = full_path('self_include.manifest')
    sourcedir = paths.containing_dir(invalid1_path)
    with mock.patch('salve.logger', dummy_logger):
        b = manifest_block.ManifestBlock(dummy_file_context,
            source=invalid1_path)
        ensure_except(block.BlockException,
                      b.expand_blocks, sourcedir, dummy_conf)


@istest
def sub_block_expand():
    """
    Unit: Manifest Block SubBlock Expand
    Verifies that Manifest block expansion works normally.
    """
    valid2_path = full_path('empty_and_file.manifest')
    sourcedir = paths.containing_dir(valid2_path)
    with mock.patch('salve.logger', dummy_logger):
        b = manifest_block.ManifestBlock(dummy_file_context,
            source=valid2_path)
        b.expand_blocks(sourcedir, dummy_conf)
    assert len(b.sub_blocks) == 2
    mblock = b.sub_blocks[0]
    fblock = b.sub_blocks[1]
    assert isinstance(mblock, manifest_block.ManifestBlock)
    assert isinstance(fblock, file_block.FileBlock)
    assert mblock.get('source') == full_path('empty.manifest')
    assert fblock.get('source') == full_path('empty.manifest')
    assert fblock.get('target') == paths.pjoin(sourcedir, 'a/b/c')


@istest
def sub_block_compile():
    """
    Unit: Manifest Block SubBlock Compile
    Verifies that Manifest block expansion followed by action
    conversion works normally.
    """
    valid2_path = full_path('empty_and_file.manifest')
    sourcedir = paths.containing_dir(valid2_path)
    with mock.patch('salve.logger', dummy_logger):
        b = manifest_block.ManifestBlock(dummy_file_context,
            source=valid2_path)
        b.expand_blocks(sourcedir, dummy_conf)
    assert len(b.sub_blocks) == 2
    mblock = b.sub_blocks[0]
    fblock = b.sub_blocks[1]
    assert isinstance(mblock, manifest_block.ManifestBlock)
    assert isinstance(fblock, file_block.FileBlock)
    assert mblock.get('source') == full_path('empty.manifest')
    assert fblock.get('source') == full_path('empty.manifest')
    assert fblock.get('target') == os.path.join(sourcedir, 'a/b/c')

    with mock.patch('salve.logger', dummy_logger):
        with mock.patch('salve.exec_context', dummy_exec_context):
            with mock.patch('os.path.exists', lambda f: True):
                with mock.patch('os.access', lambda f, p: True):
                    act = b.compile()

    assert isinstance(act, action.ActionList)
    assert len(act.actions) == 2
    assert isinstance(act.actions[0], action.ActionList)
    assert len(act.actions[0].actions) == 0
    file_act = act.actions[1]
    assert isinstance(file_act, action.ActionList)
    assert isinstance(file_act.actions[0],
                      backup.FileBackupAction)
    assert isinstance(file_act.actions[1],
                      copy.FileCopyAction)
