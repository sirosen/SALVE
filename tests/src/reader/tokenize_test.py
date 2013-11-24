#!/usr/bin/python

from nose.tools import istest
from os.path import dirname, join as pjoin

from tests.utils.exceptions import ensure_except

from src.util.error import StreamContext
import src.reader.tokenize as tokenize

_testfile_dir = pjoin(dirname(__file__),'files')

dummy_context = StreamContext('no such file',-1)

def tokenize_filename(filename):
    with open(filename) as f:
        return tokenize.tokenize_stream(f)

def get_full_path(filename):
    return pjoin(_testfile_dir,filename)

def ensure_TokenizationException(filename):
    full_path = get_full_path(filename)
    e = ensure_except(tokenize.TokenizationException,
                      tokenize_filename,
                      full_path)
    assert e.context.filename == full_path

#failure tests

@istest
def unclosed_block():
    ensure_TokenizationException('invalid1.manifest')

@istest
def missing_open():
    ensure_TokenizationException('invalid2.manifest')

@istest
def double_identifier():
    ensure_TokenizationException('invalid3.manifest')

@istest
def missing_block_identifier():
    ensure_TokenizationException('invalid4.manifest')

@istest
def missing_attribute_value():
    ensure_TokenizationException('invalid5.manifest')

@istest
def double_open():
    ensure_TokenizationException('invalid7.manifest')

#validation tests

@istest
def empty_manifest():
    tokens = tokenize_filename(get_full_path('valid1.manifest'))
    assert len(tokens) == 0

@istest
def empty_block():
    tokens = tokenize_filename(get_full_path('valid2.manifest'))
    assert len(tokens) == 3
    assert tokens[0].ty == tokenize.Token.types.IDENTIFIER
    assert tokens[1].ty == tokenize.Token.types.BLOCK_START
    assert tokens[2].ty == tokenize.Token.types.BLOCK_END

@istest
def invalid_id_nofail():
    tokens = tokenize_filename(get_full_path('invalid6.manifest'))
    assert len(tokens) == 8
    assert tokens[0].ty == tokenize.Token.types.IDENTIFIER
    assert tokens[1].ty == tokenize.Token.types.BLOCK_START
    assert tokens[2].ty == tokenize.Token.types.IDENTIFIER
    assert tokens[3].ty == tokenize.Token.types.TEMPLATE
    assert tokens[4].ty == tokenize.Token.types.BLOCK_END
    assert tokens[5].ty == tokenize.Token.types.IDENTIFIER
    assert tokens[6].ty == tokenize.Token.types.BLOCK_START
    assert tokens[7].ty == tokenize.Token.types.BLOCK_END

@istest
def attribute_with_spaces():
    tokens = tokenize_filename(get_full_path('valid3.manifest'))
    assert len(tokens) == 7
    assert tokens[0].ty == tokenize.Token.types.IDENTIFIER
    assert tokens[1].ty == tokenize.Token.types.BLOCK_START
    assert tokens[2].ty == tokenize.Token.types.IDENTIFIER
    assert tokens[3].ty == tokenize.Token.types.TEMPLATE
    assert tokens[4].ty == tokenize.Token.types.IDENTIFIER
    assert tokens[5].ty == tokenize.Token.types.TEMPLATE
    assert tokens[6].ty == tokenize.Token.types.BLOCK_END

@istest
def token_to_string():
    ctx = StreamContext('a/b/c',2)
    file_tok = tokenize.Token('file',tokenize.Token.types.IDENTIFIER,
                              ctx)
    assert str(file_tok) == 'Token(value=file,ty=IDENTIFIER,lineno=2,filename=a/b/c)'
