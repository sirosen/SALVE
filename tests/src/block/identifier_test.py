#!/usr/bin/python

from nose.tools import istest
import os, mock

from tests.utils.exceptions import ensure_except
from src.block.base_block import BlockException
from src.reader.tokenize import Token
from src.util.error import StreamContext

import src.block.file_block
import src.block.manifest_block
import src.block.directory_block
import src.block.identifier

dummy_context = StreamContext('no such file',-1)

@istest
def invalid_block_id1():
    invalid_id = Token('invalid_block_id',Token.types.IDENTIFIER,
                       dummy_context)
    ensure_except(BlockException,
                  src.block.identifier.block_from_identifier,
                  invalid_id)

@istest
def invalid_block_id2():
    invalid_id = Token('invalid_block_id',Token.types.TEMPLATE,
                       dummy_context)
    ensure_except(BlockException,
                  src.block.identifier.block_from_identifier,
                  invalid_id)

@istest
def valid_file_id():
    file_id = Token('file',Token.types.IDENTIFIER,dummy_context)
    file_block = src.block.identifier.block_from_identifier(file_id)
    assert isinstance(file_block,src.block.file_block.FileBlock)

@istest
def valid_manifest_id():
    manifest_id = Token('manifest',Token.types.IDENTIFIER,dummy_context)
    manifest_block = src.block.identifier.block_from_identifier(manifest_id)
    assert isinstance(manifest_block,src.block.manifest_block.ManifestBlock)

@istest
def valid_directory_id():
    manifest_id = Token('directory',Token.types.IDENTIFIER,dummy_context)
    dir_block = src.block.identifier.block_from_identifier(manifest_id)
    assert isinstance(dir_block,src.block.directory_block.DirBlock)
