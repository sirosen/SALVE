#!/usr/bin/python

import lib.execute.block as block
import lib.reader.parse as parse
from lib.reader.tokenize import Token

from nose.tools import istest
from os.path import dirname, join as pjoin

_testfile_dir = pjoin(dirname(__file__),'files')


def parse_filename(filename):
    with open(filename) as f:
        return parse.parse_stream(f)

def get_full_path(filename):
    return pjoin(_testfile_dir,filename)

def ensure_ParsingException(tokens=None,filename=None):
    if tokens and filename:
        raise ValueError('Invalid test: uses both tokens list and ' +\
                         'filename in ensure_ParsingException()')
    try:
        if tokens: parse.parse_tokens(tokens)
        elif filename: parse_filename(get_full_path(filename))
    except parse.ParsingException as e:
        assert tokens is None or \
               e.token is None or \
               e.token in tokens
        assert filename is None or \
               e.filename == get_full_path(filename)
    else:
        assert False

@istest
def invalid_block_id():
    invalid_id = Token('invalid_block_id',Token.types.IDENTIFIER)
    ensure_ParsingException(tokens=[invalid_id])

@istest
def invalid_block_id_from_file():
    ensure_ParsingException(filename='invalid6.manifest')

@istest
def empty_token_list():
    assert len(parse.parse_tokens([])) == 0

@istest
def unexpected_token():
    bs_tok = Token('{',Token.types.BLOCK_START)
    ensure_ParsingException(tokens=[bs_tok])

@istest
def unclosed_block1():
    file_id = Token('file',Token.types.IDENTIFIER)
    ensure_ParsingException(tokens=[file_id])

@istest
def unclosed_block2():
    file_id = Token('file',Token.types.IDENTIFIER)
    bs_tok = Token('{',Token.types.BLOCK_START)
    ensure_ParsingException(tokens=[file_id,bs_tok])

@istest
def unassigned_attr():
    file_id = Token('file',Token.types.IDENTIFIER)
    bs_tok = Token('{',Token.types.BLOCK_START)
    attr_id = Token('source',Token.types.IDENTIFIER)
    be_tok = Token('}',Token.types.BLOCK_END)
    ensure_ParsingException(tokens=[file_id,bs_tok,attr_id,be_tok])

@istest
def empty_block():
    file_id = Token('file',Token.types.IDENTIFIER)
    bs_tok = Token('{',Token.types.BLOCK_START)
    be_tok = Token('}',Token.types.BLOCK_END)
    parse.parse_tokens([file_id,bs_tok,be_tok])

@istest
def single_attr_block():
    file_id = Token('file',Token.types.IDENTIFIER)
    bs_tok = Token('{',Token.types.BLOCK_START)
    attr_id = Token('source',Token.types.IDENTIFIER)
    attr_val = Token('/tmp/txt',Token.types.TEMPLATE)
    be_tok = Token('}',Token.types.BLOCK_END)
    blocks = parse.parse_tokens([file_id,bs_tok,
                                 attr_id,attr_val,
                                 be_tok])
    assert len(blocks) == 1
    assert len(blocks[0].attrs) == 1
    assert blocks[0].attrs['source'] == '/tmp/txt'

@istest
def multiple_attr_block():
    file_id = Token('file',Token.types.IDENTIFIER)
    bs_tok = Token('{',Token.types.BLOCK_START)
    attr_id1 = Token('source',Token.types.IDENTIFIER)
    attr_val1 = Token('/tmp/txt',Token.types.TEMPLATE)
    attr_id2 = Token('target',Token.types.IDENTIFIER)
    attr_val2 = Token('/tmp/txt2',Token.types.TEMPLATE)
    be_tok = Token('}',Token.types.BLOCK_END)
    blocks = parse.parse_tokens([file_id,bs_tok,
                                 attr_id1,attr_val1,
                                 attr_id2,attr_val2,
                                 be_tok])
    assert len(blocks) == 1
    assert len(blocks[0].attrs) == 2
    assert blocks[0].attrs['source'] == '/tmp/txt'
    assert blocks[0].attrs['target'] == '/tmp/txt2'

@istest
def empty_manifest():
    blocks = parse_filename(get_full_path('valid1.manifest'))
    assert len(blocks) == 0

@istest
def empty_block():
    blocks = parse_filename(get_full_path('valid2.manifest'))
    assert len(blocks) == 1
    assert isinstance(blocks[0],block.FileBlock)
    assert len(blocks[0].attrs) == 0

@istest
def attribute_with_spaces():
    blocks = parse_filename(get_full_path('valid3.manifest'))
    assert len(blocks) == 1
    assert isinstance(blocks[0],block.FileBlock)
    assert len(blocks[0].attrs) == 2
