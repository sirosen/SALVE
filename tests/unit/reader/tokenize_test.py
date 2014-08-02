#!/usr/bin/python

from nose.tools import istest
from os.path import dirname, join as pjoin

from tests.utils.exceptions import ensure_except
from tests.utils import MockedGlobals

from salve.util.context import FileContext
from salve.reader import tokenize
from salve.util import locations

_testfile_dir = pjoin(dirname(__file__), 'files')


def tokenize_filename(filename):
    with open(filename) as f:
        return tokenize.tokenize_stream(f)


def get_full_path(filename):
    return locations.clean_path(pjoin(_testfile_dir, filename))


def ensure_TokenizationException(filename):
    full_path = get_full_path(filename)
    e = ensure_except(tokenize.TokenizationException,
                      tokenize_filename,
                      full_path)
    assert e.file_context.filename == full_path

#failure tests


class TestTokenizeMockedGlobals(MockedGlobals):
    @istest
    def unclosed_block(self):
        """
        Unit: Tokenizer Unclosed Block Fails
        Ensures that an unclosed block raises a TokenizationException.
        """
        ensure_TokenizationException('invalid1.manifest')

    @istest
    def missing_open(self):
        """
        Unit: Tokenizer Missing Block Open Fails
        Ensures that a missing { raises a TokenizationException.
        """
        ensure_TokenizationException('invalid2.manifest')

    @istest
    def missing_open_primary_attr(self):
        """
        Unit: Tokenizer Missing Block Open (Primary Attribute Block) Fails
        Ensures that a missing { raises a TokenizationException even on block's
        with a Primary Attribute setting.
        """
        ensure_TokenizationException('invalid3.manifest')

    @istest
    def missing_block_identifier(self):
        """
        Unit: Tokenizer Missing Identifier Fails
        Ensures that a missing block id raises a TokenizationException.
        """
        ensure_TokenizationException('invalid4.manifest')

    @istest
    def missing_attribute_value(self):
        """
        Unit: Tokenizer Missing Attribute Value Fails
        Ensures that a block attribute without a value raises a
        TokenizationException.
        """
        ensure_TokenizationException('invalid5.manifest')

    @istest
    def bare_identifier(self):
        """
        Unit: Tokenizer Bare Identifier Fails
        Ensures that a block without body or primary attr value raises a
        TokenizationException.
        """
        ensure_TokenizationException('invalid8.manifest')

    @istest
    def double_open(self):
        """
        Unit: Tokenizer Double Open Fails
        Ensures that repeated '{'s raise a TokenizationException.
        """
        ensure_TokenizationException('invalid7.manifest')

    #validation tests

    @istest
    def empty_manifest(self):
        """
        Unit: Tokenizer Empty Manifest
        Verifies that tokenizing an empty file produces an empty token list.
        """
        tokens = tokenize_filename(get_full_path('valid1.manifest'))
        assert len(tokens) == 0

    @istest
    def empty_block(self):
        """
        Unit: Tokenizer Empty Block
        Verifies that tokenizing an empty block produces a token list
        containing the identifier, a block open, and a block close.
        """
        tokens = tokenize_filename(get_full_path('valid2.manifest'))
        assert len(tokens) == 3
        assert tokens[0].ty == tokenize.Token.types.IDENTIFIER
        assert tokens[1].ty == tokenize.Token.types.BLOCK_START
        assert tokens[2].ty == tokenize.Token.types.BLOCK_END

    @istest
    def invalid_id_nofail(self):
        """
        Unit: Tokenizer Invalid Identifier (No Fail)
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
    def attribute_with_spaces(self):
        """
        Unit: Tokenizer Attribute With Spaces
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
    def primary_attr_block_followed_by_block(self):
        """
        Unit: Tokenizer Primary Attribute Block Followed By Normal Block
        Verifies that tokenization proceeds correctly when a "Primary
        Attribute" style block is followed by an ordinary block.
        """
        tokens = tokenize_filename(get_full_path('valid5.manifest'))
        assert len(tokens) == 9
        assert tokens[0].ty == tokenize.Token.types.IDENTIFIER
        assert tokens[1].ty == tokenize.Token.types.TEMPLATE
        assert tokens[2].ty == tokenize.Token.types.IDENTIFIER
        assert tokens[3].ty == tokenize.Token.types.BLOCK_START
        assert tokens[4].ty == tokenize.Token.types.IDENTIFIER
        assert tokens[5].ty == tokenize.Token.types.TEMPLATE
        assert tokens[6].ty == tokenize.Token.types.IDENTIFIER
        assert tokens[7].ty == tokenize.Token.types.TEMPLATE
        assert tokens[8].ty == tokenize.Token.types.BLOCK_END

    @istest
    def primary_attr_block_series(self):
        """
        Unit: Tokenizer Multiple Primary Attribute Blocks
        Verifies that tokenization proceeds correctly when a group of "Primary
        Attribute" style blocks are given in series
        """
        tokens = tokenize_filename(get_full_path('valid6.manifest'))
        assert len(tokens) == 8
        assert tokens[0].ty == tokenize.Token.types.IDENTIFIER
        assert tokens[1].ty == tokenize.Token.types.TEMPLATE
        assert tokens[2].ty == tokenize.Token.types.IDENTIFIER
        assert tokens[3].ty == tokenize.Token.types.TEMPLATE
        assert tokens[4].ty == tokenize.Token.types.IDENTIFIER
        assert tokens[5].ty == tokenize.Token.types.TEMPLATE
        assert tokens[6].ty == tokenize.Token.types.IDENTIFIER
        assert tokens[7].ty == tokenize.Token.types.TEMPLATE

    @istest
    def primary_attr_block_empty_body(self):
        """
        Unit: Tokenizer Primary Attribute Block Empty Body
        Verifies that tokenization proceeds correctly when a "Primary
        Attribute" style block is given a "{}" body
        """
        tokens = tokenize_filename(get_full_path('valid7.manifest'))
        assert len(tokens) == 4
        assert tokens[0].ty == tokenize.Token.types.IDENTIFIER
        assert tokens[1].ty == tokenize.Token.types.TEMPLATE
        assert tokens[2].ty == tokenize.Token.types.BLOCK_START
        assert tokens[3].ty == tokenize.Token.types.BLOCK_END

    @istest
    def token_to_string(self):
        """
        Unit: Tokenizer Token To String
        Checks the result of invoking Token.__str__
        """
        ctx = FileContext('a/b/c', 2)
        file_tok = tokenize.Token('file', tokenize.Token.types.IDENTIFIER, ctx)
        assert str(file_tok) == \
                'Token(value=file,ty=IDENTIFIER,lineno=2,filename=a/b/c)'
