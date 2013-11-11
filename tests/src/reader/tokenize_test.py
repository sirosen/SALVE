#!/usr/bin/python

import src.reader.tokenize as tokenize

from nose.tools import istest
from os.path import dirname, join as pjoin

_testfile_dir = pjoin(dirname(__file__),'files')

def tokenize_filename(filename):
    with open(filename) as f:
        return tokenize.tokenize_stream(f)

def get_full_path(filename):
    return pjoin(_testfile_dir,filename)

def ensure_TokenizationException(filename):
    full_path = get_full_path(filename)
    try:
        tokenize_filename(full_path)
        # Should never reach this, we are trying a bad file
        assert False
    except tokenize.TokenizationException as e:
        assert e.filename is None or \
               e.filename == full_path
    else:
        assert False

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
