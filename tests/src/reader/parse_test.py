#!/usr/bin/python

from nose.tools import istest
from os.path import dirname, join as pjoin

import src.block.file_block
import src.reader.parse as parse
from src.reader.tokenize import Token
from src.util.error import StreamContext

from tests.utils.exceptions import ensure_except

_testfile_dir = pjoin(dirname(__file__),'files')
dummy_context = StreamContext('no such file',-1)

def parse_filename(filename):
    with open(filename) as f:
        return parse.parse_stream(f)

def get_full_path(filename):
    return pjoin(_testfile_dir,filename)

def ensure_ParsingException(tokens=None,filename=None):
    if tokens and filename:
        raise ValueError('Invalid test: uses both tokens list and ' +\
                         'filename in ensure_ParsingException()')
    e = None
    if tokens:
        e = ensure_except(parse.ParsingException,
                          parse.parse_tokens,
                          tokens)
    elif filename:
        e = ensure_except(parse.ParsingException,
                          parse_filename,
                          get_full_path(filename))
    else:
        assert False
    assert filename is None or \
           e.context.filename == get_full_path(filename)

@istest
def invalid_block_id():
    invalid_id = Token('invalid_block_id',Token.types.IDENTIFIER,
                       dummy_context)
    ensure_ParsingException(tokens=[invalid_id])

@istest
def invalid_block_id_from_file():
    ensure_ParsingException(filename='invalid6.manifest')

@istest
def empty_token_list():
    assert len(parse.parse_tokens([])) == 0

@istest
def unexpected_token():
    bs_tok = Token('{',Token.types.BLOCK_START,dummy_context)
    ensure_ParsingException(tokens=[bs_tok])

@istest
def unclosed_block1():
    file_id = Token('file',Token.types.IDENTIFIER,dummy_context)
    ensure_ParsingException(tokens=[file_id])

@istest
def unclosed_block2():
    file_id = Token('file',Token.types.IDENTIFIER,dummy_context)
    bs_tok = Token('{',Token.types.BLOCK_START,dummy_context)
    ensure_ParsingException(tokens=[file_id,bs_tok])

@istest
def unassigned_attr():
    file_id = Token('file',Token.types.IDENTIFIER,dummy_context)
    bs_tok = Token('{',Token.types.BLOCK_START,dummy_context)
    attr_id = Token('source',Token.types.IDENTIFIER,dummy_context)
    be_tok = Token('}',Token.types.BLOCK_END,dummy_context)
    ensure_ParsingException(tokens=[file_id,bs_tok,attr_id,be_tok])

@istest
def empty_block():
    file_id = Token('file',Token.types.IDENTIFIER,dummy_context)
    bs_tok = Token('{',Token.types.BLOCK_START,dummy_context)
    be_tok = Token('}',Token.types.BLOCK_END,dummy_context)
    parse.parse_tokens([file_id,bs_tok,be_tok])

@istest
def single_attr_block():
    file_id = Token('file',Token.types.IDENTIFIER,dummy_context)
    bs_tok = Token('{',Token.types.BLOCK_START,dummy_context)
    attr_id = Token('source',Token.types.IDENTIFIER,dummy_context)
    attr_val = Token('/tmp/txt',Token.types.TEMPLATE,dummy_context)
    be_tok = Token('}',Token.types.BLOCK_END,dummy_context)
    blocks = parse.parse_tokens([file_id,bs_tok,
                                 attr_id,attr_val,
                                 be_tok])
    assert len(blocks) == 1
    assert len(blocks[0].attrs) == 1
    assert blocks[0].get('source') == '/tmp/txt'

@istest
def multiple_attr_block():
    file_id = Token('file',Token.types.IDENTIFIER,dummy_context)
    bs_tok = Token('{',Token.types.BLOCK_START,dummy_context)
    attr_id1 = Token('source',Token.types.IDENTIFIER,dummy_context)
    attr_val1 = Token('/tmp/txt',Token.types.TEMPLATE,dummy_context)
    attr_id2 = Token('target',Token.types.IDENTIFIER,dummy_context)
    attr_val2 = Token('/tmp/txt2',Token.types.TEMPLATE,dummy_context)
    be_tok = Token('}',Token.types.BLOCK_END,dummy_context)
    blocks = parse.parse_tokens([file_id,bs_tok,
                                 attr_id1,attr_val1,
                                 attr_id2,attr_val2,
                                 be_tok])
    assert len(blocks) == 1
    assert len(blocks[0].attrs) == 2
    assert blocks[0].get('source') == '/tmp/txt'
    assert blocks[0].get('target') == '/tmp/txt2'

@istest
def empty_manifest():
    blocks = parse_filename(get_full_path('valid1.manifest'))
    assert len(blocks) == 0

@istest
def empty_block():
    blocks = parse_filename(get_full_path('valid2.manifest'))
    assert len(blocks) == 1
    assert isinstance(blocks[0],src.block.file_block.FileBlock)
    assert len(blocks[0].attrs) == 0

@istest
def attribute_with_spaces():
    blocks = parse_filename(get_full_path('valid3.manifest'))
    assert len(blocks) == 1
    assert isinstance(blocks[0],src.block.file_block.FileBlock)
    assert len(blocks[0].attrs) == 2
