#!/usr/bin/python

from nose.tools import istest
from os.path import dirname, join as pjoin

import src.block.file_block

import src.reader.tokenize
import src.reader.parse

from tests.utils.exceptions import ensure_except

_testfile_dir = pjoin(dirname(__file__),'files')

def parse_filename(filename):
    with open(filename) as f:
        return src.reader.parse.parse_stream(f)

def get_full_path(filename):
    return pjoin(_testfile_dir,filename)

@istest
def empty_file():
    """
    E2E: Parse Empty Manifest File

    Checks that parsing an empty file produces an empty list of blocks.
    """
    blocks = parse_filename(get_full_path('valid1.manifest'))
    assert len(blocks) == 0

@istest
def empty_block():
    """
    E2E: Parse File With Empty Block

    Checks that parsing an empty block raises no errors.
    """
    blocks = parse_filename(get_full_path('valid2.manifest'))
    assert len(blocks) == 1
    fblock = blocks[0]
    assert isinstance(fblock,src.block.file_block.FileBlock)

@istest
def single_attr_block():
    """
    E2E: Parse File With Single Attr Block

    Checks that parsing a block with one attribute raises no errors.
    """
    blocks = parse_filename(get_full_path('valid3.manifest'))
    assert len(blocks) == 1
    fblock = blocks[0]
    assert isinstance(fblock,src.block.file_block.FileBlock)
    assert fblock.get('source') == '/a/b/c'

@istest
def multiple_attr_block():
    """
    E2E: Parse File With Multiple Attr Block

    Checks that parsing a block with several attributes raises no
    errors.
    """
    blocks = parse_filename(get_full_path('valid4.manifest'))
    assert len(blocks) == 1
    fblock = blocks[0]
    assert isinstance(fblock,src.block.file_block.FileBlock)
    assert fblock.get('source') == '/a/b/c'
    assert fblock.get('target') == '/d/e'

@istest
def spaced_attr_block():
    """
    E2E: Parse File With Block Attr Containing Spaces

    Checks that parsing a block with several attributes raises no
    errors.
    """
    blocks = parse_filename(get_full_path('valid5.manifest'))
    assert len(blocks) == 1
    fblock = blocks[0]
    assert isinstance(fblock,src.block.file_block.FileBlock)
    assert fblock.get('source') == '/a/b/c'
    assert fblock.get('target') == '/d/e f/g'

@istest
def unclosed_block_raises_TE():
    """
    E2E: Parse File With Unclosed Block Raises Tokenization Exception

    Not only validates that a Tokenization Exception occurs, but also
    verifies the context of the raised exception.
    """
    path = get_full_path('invalid1.manifest')
    e = ensure_except(src.reader.tokenize.TokenizationException,
                      parse_filename,
                      path)
    ctx = e.context
    assert ctx.lineno == 4
    assert ctx.filename == path

@istest
def missing_open_raises_TE():
    """
    E2E: Parse File With Unopened Block Raises Tokenization Exception

    Not only validates that a Tokenization Exception occurs, but also
    verifies the context of the raised exception.
    """
    path = get_full_path('invalid2.manifest')
    e = ensure_except(src.reader.tokenize.TokenizationException,
                      parse_filename,
                      path)
    ctx = e.context
    assert ctx.lineno == 5
    assert ctx.filename == path

@istest
def double_identifier_raises_TE():
    """
    E2E: Parse File With Repeated Block ID Raises Tokenization Exception

    Not only validates that a Tokenization Exception occurs, but also
    verifies the context of the raised exception.
    """
    path = get_full_path('invalid3.manifest')
    e = ensure_except(src.reader.tokenize.TokenizationException,
                      parse_filename,
                      path)
    ctx = e.context
    assert ctx.lineno == 5
    assert ctx.filename == path

@istest
def missing_identifier_raises_TE():
    """
    E2E: Parse File With Missing Block ID Raises Tokenization Exception

    Not only validates that a Tokenization Exception occurs, but also
    verifies the context of the raised exception.
    """
    path = get_full_path('invalid4.manifest')
    e = ensure_except(src.reader.tokenize.TokenizationException,
                      parse_filename,
                      path)
    ctx = e.context
    assert ctx.lineno == 3
    assert ctx.filename == path

@istest
def missing_value_raises_TE():
    """
    E2E: Parse File With Missing Block ID Raises Tokenization Exception

    Not only validates that a Tokenization Exception occurs, but also
    verifies the context of the raised exception.
    """
    path = get_full_path('invalid5.manifest')
    e = ensure_except(src.reader.tokenize.TokenizationException,
                      parse_filename,
                      path)
    ctx = e.context
    assert ctx.lineno == 5
    assert ctx.filename == path

@istest
def double_open_raises_TE():
    """
    E2E: Parse File With Double Block Open Raises Tokenization Exception

    Not only validates that a Tokenization Exception occurs, but also
    verifies the context of the raised exception.
    """
    path = get_full_path('invalid7.manifest')
    e = ensure_except(src.reader.tokenize.TokenizationException,
                      parse_filename,
                      path)
    ctx = e.context
    assert ctx.lineno == 3
    assert ctx.filename == path

@istest
def invalid_block_id_raises_PE():
    """
    E2E: Parse File With Invalid Block ID Raises Parsing Exception

    Not only validates that a Tokenization Exception occurs, but also
    verifies the context of the raised exception.
    """
    path = get_full_path('invalid6.manifest')
    e = ensure_except(src.reader.parse.ParsingException,
                      parse_filename,
                      path)
    ctx = e.context
    assert ctx.lineno == 7
    assert ctx.filename == path
