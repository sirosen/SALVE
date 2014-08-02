#!/usr/bin/python

from nose.tools import istest
from os.path import dirname, join as pjoin

from salve.reader import parse
from salve.reader.tokenize import Token
from salve.util.context import FileContext
from salve.util import locations

from tests.utils.exceptions import ensure_except
from tests.utils import MockedGlobals

import salve.block.file_block
import salve.block.manifest_block

_testfile_dir = pjoin(dirname(__file__), 'files')
dummy_context = FileContext('no such file')


def parse_filename(filename):
    with open(filename) as f:
        return parse.parse_stream(f)


def get_full_path(filename):
    return locations.clean_path(pjoin(_testfile_dir, filename))


def ensure_ParsingException(tokens=None, filename=None):
    if tokens and filename:
        raise ValueError('Invalid test: uses both tokens list and ' +
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
           e.file_context.filename == get_full_path(filename)


class TestParsingMockedGlobals(MockedGlobals):
    @istest
    def invalid_block_id(self):
        """
        Unit: Parser Invalid Block Identifier
        Verifies that attempting to parse a token stream containing an
        unknown block identifier raises a ParsingException.
        """
        invalid_id = Token('invalid_block_id', Token.types.IDENTIFIER,
                           dummy_context)
        ensure_ParsingException(tokens=[invalid_id])

    @istest
    def invalid_block_id_from_file(self):
        """
        Unit: Parser Invalid Block Identifier From File
        Verifies that attempting to parse a file containing an unknown
        block identifier raises a ParsingException.
        """
        ensure_ParsingException(filename='invalid6.manifest')

    @istest
    def empty_token_list(self):
        """
        Unit: Parser Empty Token List
        Checks that parsing an empty token list produces an empty list of
        blocks.
        """
        assert len(parse.parse_tokens([])) == 0

    @istest
    def unexpected_token(self):
        """
        Unit: Parser Unexpected Token
        Checks that parsing a token list with a token that violates the
        SALVE grammar raises a ParsingException.
        """
        bs_tok = Token('{', Token.types.BLOCK_START, dummy_context)
        ensure_ParsingException(tokens=[bs_tok])

    @istest
    def unclosed_block1(self):
        """
        Unit: Parser Partial Block Fails (No Open)
        Checks that parsing a token list with an unclosed block raises a
        ParsingException.
        """
        file_id = Token('file', Token.types.IDENTIFIER, dummy_context)
        ensure_ParsingException(tokens=[file_id])

    @istest
    def unclosed_block2(self):
        """
        Unit: Parser Partial Block Fails (No Close)
        Checks that parsing a token list with an unclosed block raises a
        ParsingException.
        """
        file_id = Token('file', Token.types.IDENTIFIER, dummy_context)
        bs_tok = Token('{', Token.types.BLOCK_START, dummy_context)
        ensure_ParsingException(tokens=[file_id, bs_tok])

    @istest
    def unassigned_attr(self):
        """
        Unit: Parser Unassigned Attribute Fails
        Checks that parsing a block with an attribute that is declared but
        is followed by a block close raises a ParsingException.
        """
        file_id = Token('file', Token.types.IDENTIFIER, dummy_context)
        bs_tok = Token('{', Token.types.BLOCK_START, dummy_context)
        attr_id = Token('source', Token.types.IDENTIFIER, dummy_context)
        be_tok = Token('}', Token.types.BLOCK_END, dummy_context)
        ensure_ParsingException(tokens=[file_id, bs_tok, attr_id, be_tok])

    @istest
    def empty_block(self):
        """
        Unit: Parser Empty Block
        Checks that parsing an empty block raises no errors.
        """
        file_id = Token('file', Token.types.IDENTIFIER, dummy_context)
        bs_tok = Token('{', Token.types.BLOCK_START, dummy_context)
        be_tok = Token('}', Token.types.BLOCK_END, dummy_context)
        parse.parse_tokens([file_id, bs_tok, be_tok])

    @istest
    def single_attr_block(self):
        """
        Unit: Parser Empty Block
        Checks that parsing a block with one attribute raises no errors.
        """
        file_id = Token('file', Token.types.IDENTIFIER, dummy_context)
        bs_tok = Token('{', Token.types.BLOCK_START, dummy_context)
        attr_id = Token('source', Token.types.IDENTIFIER, dummy_context)
        attr_val = Token('/tmp/txt', Token.types.TEMPLATE, dummy_context)
        be_tok = Token('}', Token.types.BLOCK_END, dummy_context)
        blocks = parse.parse_tokens([file_id, bs_tok,
                                     attr_id, attr_val,
                                     be_tok])
        assert len(blocks) == 1
        assert len(blocks[0].attrs) == 1
        assert blocks[0].get('source') == '/tmp/txt'

    @istest
    def multiple_attr_block(self):
        """
        Unit: Parser Empty Block
        Checks that parsing a block with several attributes raises no
        errors.
        """
        file_id = Token('file', Token.types.IDENTIFIER, dummy_context)
        bs_tok = Token('{', Token.types.BLOCK_START, dummy_context)
        attr_id1 = Token('source', Token.types.IDENTIFIER, dummy_context)
        attr_val1 = Token('/tmp/txt', Token.types.TEMPLATE, dummy_context)
        attr_id2 = Token('target', Token.types.IDENTIFIER, dummy_context)
        attr_val2 = Token('/tmp/txt2', Token.types.TEMPLATE, dummy_context)
        be_tok = Token('}', Token.types.BLOCK_END, dummy_context)
        blocks = parse.parse_tokens([file_id, bs_tok,
                                     attr_id1, attr_val1,
                                     attr_id2, attr_val2,
                                     be_tok])
        assert len(blocks) == 1
        assert len(blocks[0].attrs) == 2
        assert blocks[0].get('source') == '/tmp/txt'
        assert blocks[0].get('target') == '/tmp/txt2'

    @istest
    def empty_manifest(self):
        """
        Unit: Parser Empty File
        Checks that parsing an empty file produces an empty block list.
        """
        blocks = parse_filename(get_full_path('valid1.manifest'))
        assert len(blocks) == 0

    @istest
    def empty_block(self):
        """
        Unit: Parser Empty Block In File
        Checks that parsing a file with an empty block is valid.
        """
        blocks = parse_filename(get_full_path('valid2.manifest'))
        assert len(blocks) == 1
        assert isinstance(blocks[0], salve.block.file_block.FileBlock)
        assert len(blocks[0].attrs) == 0

    @istest
    def attribute_with_spaces(self):
        """
        Unit: Parser Attribute With Spaces
        Checks that parsing an attribute that contains spaces in quotes
        does not raise an error and correctly assigns to the attribute.
        """
        blocks = parse_filename(get_full_path('valid3.manifest'))
        assert len(blocks) == 1
        assert isinstance(blocks[0], salve.block.file_block.FileBlock)
        assert len(blocks[0].attrs) == 2

    @istest
    def file_primary_attr_assigned(self):
        """
        Unit: Parser File Block Primary Attr
        Checks that parsing a Primary Attribute style file block does not raise
        any errors.
        """
        blocks = parse_filename(get_full_path('valid4.manifest'))
        assert len(blocks) == 1
        assert isinstance(blocks[0], salve.block.file_block.FileBlock)
        assert len(blocks[0].attrs) == 2
        assert blocks[0].get(blocks[0].primary_attr) == "/d/e/f/g"

    @istest
    def primary_attr_followed_by_block(self):
        """
        Unit: Parser Primary Attribute Block Followed By Normal Block
        Checks that there are no errors parsing a Primary Attribute style block
        followed by an ordinary block.
        """
        blocks = parse_filename(get_full_path('valid5.manifest'))
        assert len(blocks) == 2
        assert isinstance(blocks[0], salve.block.manifest_block.ManifestBlock)
        assert len(blocks[0].attrs) == 1
        assert blocks[0].get(blocks[0].primary_attr) == "man man"
        assert isinstance(blocks[1], salve.block.file_block.FileBlock)
        assert len(blocks[1].attrs) == 2
        assert blocks[1].get('source') == "potato"
        assert blocks[1].get('target') == "mango"

    @istest
    def file_primary_attr_with_body(self):
        """
        Unit: Parser File Block Primary Attr And Block Body
        Checks that parsing is successful on a primary attr block with a
        nonempty body.
        """
        blocks = parse_filename(get_full_path('valid8.manifest'))
        assert len(blocks) == 1
        assert isinstance(blocks[0], salve.block.file_block.FileBlock)
        assert len(blocks[0].attrs) == 2
        assert blocks[0].get(blocks[0].primary_attr) == "lobster"
        assert blocks[0].get('source') == "salad"
