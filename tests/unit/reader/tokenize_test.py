#!/usr/bin/python

from nose.tools import istest
from os.path import dirname, join as pjoin

from tests.utils.exceptions import ensure_except

from src.util.context import SALVEContext, StreamContext, ExecutionContext
import src.reader.tokenize as tokenize
import src.util.locations as locations

_testfile_dir = pjoin(dirname(__file__),'files')

dummy_stream_context = StreamContext('no such file',-1)
dummy_exec_context = ExecutionContext(
    startphase=ExecutionContext.phases.PARSING
)
dummy_context = SALVEContext(stream_context=dummy_stream_context,
                             exec_context=dummy_exec_context)

def tokenize_filename(filename):
    with open(filename) as f:
        return tokenize.tokenize_stream(dummy_context,f)

def get_full_path(filename):
    return locations.clean_path(pjoin(_testfile_dir,filename))

def ensure_TokenizationException(filename):
    full_path = get_full_path(filename)
    e = ensure_except(tokenize.TokenizationException,
                      tokenize_filename,
                      full_path)
    assert e.context.stream_context.filename == full_path

#failure tests

@istest
def unclosed_block():
    """
    Tokenizer Unclosed Block Fails
    Ensures that an unclosed block raises a TokenizationException.
    """
    ensure_TokenizationException('invalid1.manifest')

@istest
def missing_open():
    """
    Tokenizer Missing Block Open Fails
    Ensures that a missing { raises a TokenizationException.
    """
    ensure_TokenizationException('invalid2.manifest')

@istest
def double_identifier():
    """
    Tokenizer Double Identifier Fails
    Ensures that two successive block ids raise a TokenizationException.
    """
    ensure_TokenizationException('invalid3.manifest')

@istest
def missing_block_identifier():
    """
    Tokenizer Missing Identifier Fails
    Ensures that a missing block id raises a TokenizationException.
    """
    ensure_TokenizationException('invalid4.manifest')

@istest
def missing_attribute_value():
    """
    Tokenizer Missing Attribute Value Fails
    Ensures that a block attribute without a value raises a
    TokenizationException.
    """
    ensure_TokenizationException('invalid5.manifest')

@istest
def double_open():
    """
    Tokenizer Double Open Fails
    Ensures that repeated '{'s raise a TokenizationException.
    """
    ensure_TokenizationException('invalid7.manifest')

#validation tests

@istest
def empty_manifest():
    """
    Tokenizer Empty Manifest
    Verifies that tokenizing an empty file produces an empty token list.
    """
    tokens = tokenize_filename(get_full_path('valid1.manifest'))
    assert len(tokens) == 0

@istest
def empty_block():
    """
    Tokenizer Empty Block
    Verifies that tokenizing an empty block produces a token list
    containing the identifier, a block open, and a block close.
    """
    tokens = tokenize_filename(get_full_path('valid2.manifest'))
    assert len(tokens) == 3
    assert tokens[0].ty == tokenize.Token.types.IDENTIFIER
    assert tokens[1].ty == tokenize.Token.types.BLOCK_START
    assert tokens[2].ty == tokenize.Token.types.BLOCK_END

@istest
def invalid_id_nofail():
    """
    Tokenizer Invalid Identifier (No Fail)
    Ensures that no exception is raised if the tokenizer encounters an
    unknown block identifier.
    """
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
    """
    Tokenizer Attribute With Spaces
    Verifies that tokenization proceeds correctly when an attribute
    value is a quoted string containing spaces.
    """
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
    """
    Tokenizer Token To String
    Checks the result of invoking Token.__str__
    """
    ctx = SALVEContext(stream_context=StreamContext('a/b/c',2))
    file_tok = tokenize.Token('file',tokenize.Token.types.IDENTIFIER,
                              ctx)
    assert str(file_tok) == 'Token(value=file,ty=IDENTIFIER,lineno=2,filename=a/b/c)'
