#!/usr/bin/python

from nose.tools import istest

from salve import paths
from salve.parser import parse, Token
from salve.context import FileContext
from salve.block import FileBlock, ManifestBlock

from tests.util import ensure_except, full_path, MockedGlobals

dummy_context = FileContext('no such file')


def parse_filename(filename):
    with open(filename) as f:
        return parse.parse_stream(f)


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
                          full_path(filename))
    else:
        assert False
    assert (filename is None or
            paths.clean_path(e.file_context.filename) ==
            paths.clean_path(full_path(filename)))


def _generate_tokens(*args):
    return [Token(name, ty, dummy_context) for (name, ty) in args]


def _check_blocks(block_list, *args):
    assert len(block_list) == len(args)

    for (i, (ty, num_attrs)) in enumerate(args):
        assert isinstance(block_list[i], ty)
        assert len(block_list[i].attrs) == num_attrs


class TestParsingMockedGlobals(MockedGlobals):
    @istest
    def invalid_block_id(self):
        """
        Unit: Parser Invalid Block Identifier
        Verifies that attempting to parse a token stream containing an
        unknown block identifier raises a ParsingException.
        """
        ensure_ParsingException(tokens=_generate_tokens(
            ('invalid_block_id', Token.types.IDENTIFIER)))

    @istest
    def invalid_block_id_from_file(self):
        """
        Unit: Parser Invalid Block Identifier From File
        Verifies that attempting to parse a file containing an unknown
        block identifier raises a ParsingException.
        """
        ensure_ParsingException(filename='invalid_block_id.manifest')

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
        ensure_ParsingException(tokens=_generate_tokens(
            ('{', Token.types.BLOCK_START)))

    @istest
    def unclosed_block1(self):
        """
        Unit: Parser Partial Block Fails (No Open)
        Checks that parsing a token list with an unclosed block raises a
        ParsingException.
        """
        ensure_ParsingException(tokens=_generate_tokens(
            ('file', Token.types.IDENTIFIER)))

    @istest
    def unclosed_block2(self):
        """
        Unit: Parser Partial Block Fails (No Close)
        Checks that parsing a token list with an unclosed block raises a
        ParsingException.
        """
        ensure_ParsingException(tokens=_generate_tokens(
            ('file', Token.types.IDENTIFIER), ('{', Token.types.BLOCK_START)))

    @istest
    def unassigned_attr(self):
        """
        Unit: Parser Unassigned Attribute Fails
        Checks that parsing a block with an attribute that is declared but
        is followed by a block close raises a ParsingException.
        """
        ensure_ParsingException(tokens=_generate_tokens(
            ('file', Token.types.IDENTIFIER), ('{', Token.types.BLOCK_START),
            ('source', Token.types.IDENTIFIER), ('}', Token.types.BLOCK_END)
        ))

    @istest
    def empty_block(self):
        """
        Unit: Parser Empty Block
        Checks that parsing an empty block raises no errors.
        """
        parse.parse_tokens(_generate_tokens(
            ('file', Token.types.IDENTIFIER), ('{', Token.types.BLOCK_START),
            ('}', Token.types.BLOCK_END)
        ))

    @istest
    def single_attr_block(self):
        """
        Unit: Parser Empty Block
        Checks that parsing a block with one attribute raises no errors.
        """
        blocks = parse.parse_tokens(_generate_tokens(
            ('file', Token.types.IDENTIFIER), ('{', Token.types.BLOCK_START),
            ('source', Token.types.IDENTIFIER),
            ('/tmp/txt', Token.types.TEMPLATE), ('}', Token.types.BLOCK_END)
        ))
        _check_blocks(blocks, (FileBlock, 1))
        assert blocks[0]['source'] == '/tmp/txt'

    @istest
    def multiple_attr_block(self):
        """
        Unit: Parser Empty Block
        Checks that parsing a block with several attributes raises no
        errors.
        """
        blocks = parse.parse_tokens(_generate_tokens(
            ('file', Token.types.IDENTIFIER), ('{', Token.types.BLOCK_START),
            ('source', Token.types.IDENTIFIER),
            ('/tmp/txt', Token.types.TEMPLATE),
            ('target', Token.types.IDENTIFIER),
            ('/tmp/txt2', Token.types.TEMPLATE),
            ('}', Token.types.BLOCK_END)
        ))
        _check_blocks(blocks, (FileBlock, 2))
        assert blocks[0]['source'] == '/tmp/txt'
        assert blocks[0]['target'] == '/tmp/txt2'

    @istest
    def empty_manifest(self):
        """
        Unit: Parser Empty File
        Checks that parsing an empty file produces an empty block list.
        """
        blocks = parse_filename(full_path('empty.manifest'))
        _check_blocks(blocks)

    @istest
    def empty_block_in_file(self):
        """
        Unit: Parser Empty Block In File
        Checks that parsing a file with an empty block is valid.
        """
        blocks = parse_filename(full_path('empty_block.manifest'))
        _check_blocks(blocks, (FileBlock, 0))

    @istest
    def attribute_with_spaces(self):
        """
        Unit: Parser Attribute With Spaces
        Checks that parsing an attribute that contains spaces in quotes
        does not raise an error and correctly assigns to the attribute.
        """
        blocks = parse_filename(full_path('spaced_attr.manifest'))
        _check_blocks(blocks, (FileBlock, 2))

    @istest
    def file_primary_attr_assigned(self):
        """
        Unit: Parser File Block Primary Attr
        Checks that parsing a Primary Attribute style file block does not raise
        any errors.
        """
        blocks = parse_filename(full_path('primary_attr.manifest'))
        _check_blocks(blocks, (FileBlock, 2))
        assert blocks[0][blocks[0].primary_attr] == "/d/e/f/g"

    @istest
    def primary_attr_followed_by_block(self):
        """
        Unit: Parser Primary Attribute Block Followed By Normal Block
        Checks that there are no errors parsing a Primary Attribute style block
        followed by an ordinary block.
        """
        blocks = parse_filename(full_path('primary_attr2.manifest'))
        _check_blocks(blocks, (ManifestBlock, 1), (FileBlock, 2))
        assert blocks[0][blocks[0].primary_attr] == "man man"
        assert blocks[1]['source'] == "potato"
        assert blocks[1]['target'] == "mango"

    @istest
    def file_primary_attr_with_body(self):
        """
        Unit: Parser File Block Primary Attr And Block Body
        Checks that parsing is successful on a primary attr block with a
        nonempty body.
        """
        blocks = parse_filename(full_path('primary_attr5.manifest'))
        _check_blocks(blocks, (FileBlock, 2))
        assert blocks[0][blocks[0].primary_attr] == "lobster"
        assert blocks[0]['source'] == "salad"
