#!/usr/bin/python

import os
import mock
from nose.tools import istest

from tests.utils.exceptions import ensure_except
from salve.block.base import BlockException
from salve.reader.tokenize import Token

import salve.block.file_block
import salve.block.manifest_block
import salve.block.directory_block
import salve.block.identifier

from tests.unit.block import dummy_context, dummy_stream_context, dummy_logger


@istest
def invalid_block_id1():
    """
    Block Identifier Invalid Identifier Fails (1)
    Checks that an invalid block identifier fails, even when it is of
    type IDENTIFIER.
    """
    invalid_id = Token('invalid_block_id', Token.types.IDENTIFIER,
            dummy_context)

    with mock.patch('salve.logger', dummy_logger):
        ensure_except(BlockException,
                      salve.block.identifier.block_from_identifier,
                      dummy_context, invalid_id)


@istest
def invalid_block_id2():
    """
    Block Identifier Invalid Identifier Fails (2)
    Checks that an invalid block identifier with a non-IDENTIFIER type
    fails block creation.
    """
    invalid_id = Token('invalid_block_id', Token.types.TEMPLATE,
                       dummy_context)

    with mock.patch('salve.logger', dummy_logger):
        ensure_except(BlockException,
                      salve.block.identifier.block_from_identifier,
                      dummy_context, invalid_id)


@istest
def valid_file_id():
    """
    Block Identifier File Identifier To Block
    Checks that an identifier 'file' creates a file block.
    """
    file_id = Token('file', Token.types.IDENTIFIER, dummy_context)
    with mock.patch('salve.logger', dummy_logger):
        file_block = salve.block.identifier.block_from_identifier(
                dummy_context, file_id)
    assert isinstance(file_block, salve.block.file_block.FileBlock)


@istest
def valid_manifest_id():
    """
    Block Identifier Manifest Identifier To Block
    Checks that an identifier 'manifest' creates a manifest block.
    """
    manifest_id = Token('manifest', Token.types.IDENTIFIER, dummy_context)
    with mock.patch('salve.logger', dummy_logger):
        manifest_block = salve.block.identifier.block_from_identifier(
            dummy_context, manifest_id)
    assert isinstance(manifest_block, salve.block.manifest_block.ManifestBlock)


@istest
def valid_directory_id():
    """
    Block Identifier Directory Identifier To Block
    Checks that an identifier 'directory' creates a directory block.
    """
    manifest_id = Token('directory', Token.types.IDENTIFIER, dummy_context)
    with mock.patch('salve.logger', dummy_logger):
        dir_block = salve.block.identifier.block_from_identifier(dummy_context,
            manifest_id)
    assert isinstance(dir_block, salve.block.directory_block.DirBlock)
