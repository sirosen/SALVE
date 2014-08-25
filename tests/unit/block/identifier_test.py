#!/usr/bin/python

import os
import mock
from nose.tools import istest

from tests.util import ensure_except
from salve.reader.tokenize import Token

from salve.block import BlockException, identifier, \
        file_block, manifest_block, directory_block

from tests.unit.block import dummy_file_context, dummy_logger


@istest
def invalid_block_id1():
    """
    Unit: Block Identifier Invalid Identifier Fails (1)
    Checks that an invalid block identifier fails, even when it is of
    type IDENTIFIER.
    """
    invalid_id = Token('invalid_block_id', Token.types.IDENTIFIER,
            dummy_file_context)

    with mock.patch('salve.logger', dummy_logger):
        ensure_except(BlockException,
                      identifier.block_from_identifier,
                      invalid_id)


@istest
def invalid_block_id2():
    """
    Unit: Block Identifier Invalid Identifier Fails (2)
    Checks that an invalid block identifier with a non-IDENTIFIER type
    fails block creation.
    """
    invalid_id = Token('invalid_block_id', Token.types.TEMPLATE,
                       dummy_file_context)

    with mock.patch('salve.logger', dummy_logger):
        ensure_except(BlockException,
                      identifier.block_from_identifier,
                      invalid_id)


@istest
def valid_file_id():
    """
    Unit: Block Identifier File Identifier To Block
    Checks that an identifier 'file' creates a file block.
    """
    file_id = Token('file', Token.types.IDENTIFIER, dummy_file_context)
    with mock.patch('salve.logger', dummy_logger):
        fb = identifier.block_from_identifier(file_id)
    assert isinstance(fb, file_block.FileBlock)


@istest
def valid_manifest_id():
    """
    Unit: Block Identifier Manifest Identifier To Block
    Checks that an identifier 'manifest' creates a manifest block.
    """
    manifest_id = Token('manifest', Token.types.IDENTIFIER, dummy_file_context)
    with mock.patch('salve.logger', dummy_logger):
        mb = identifier.block_from_identifier(
                manifest_id)
    assert isinstance(mb, manifest_block.ManifestBlock)


@istest
def valid_directory_id():
    """
    Unit: Block Identifier Directory Identifier To Block
    Checks that an identifier 'directory' creates a directory block.
    """
    manifest_id = Token('directory', Token.types.IDENTIFIER,
            dummy_file_context)
    with mock.patch('salve.logger', dummy_logger):
        dir_block = identifier.block_from_identifier(manifest_id)
    assert isinstance(dir_block, directory_block.DirBlock)
