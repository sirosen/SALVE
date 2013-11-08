#!/usr/bin/python

from nose.tools import istest

from lib.parse.tokenize import Token
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
