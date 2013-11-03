#!/usr/bin/python

import tokenize
from nose.tools import istest

from os.path import dirname, join as pjoin
_testfile_dir = pjoin(dirname(__file__),'testfiles')

def tokenize_filename(filename):
    with open(pjoin(_testfile_dir,filename)) as f:
        return tokenize.tokenize_stream(f)

def ensure_TokenizationException(filename):
    try:
        tokenize_filename(filename)
        # Should never reach this, we are trying a bad file
        assert False
    except tokenize.TokenizationException:
        pass
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
    tokens = tokenize_filename('valid1.manifest')
    assert len(tokens) == 0

@istest
def empty_block():
    tokens = tokenize_filename('valid2.manifest')
    assert len(tokens) == 3
    assert tokens[0].token_type == tokenize.token_tys.IDENTIFIER
    assert tokens[1].token_type == tokenize.token_tys.BLOCK_START
    assert tokens[2].token_type == tokenize.token_tys.BLOCK_END
