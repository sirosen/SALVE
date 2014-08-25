#!/usr/bin/python

from nose.tools import istest

from salve import paths
from salve.block import file_block
from salve.reader import tokenize, parse

from tests.util import scratch, ensure_except, full_path


def parse_filename(filename):
    with open(filename) as f:
        return parse.parse_stream(f)


class TestWithScratchContainer(scratch.ScratchContainer):
    @istest
    def empty_file(self):
        """
        Integration: Parse Empty Manifest File

        Checks that parsing an empty file produces an empty list of blocks.
        """
        blocks = parse_filename(full_path('empty.manifest'))
        assert len(blocks) == 0

    @istest
    def empty_block(self):
        """
        Integration: Parse File With Empty Block

        Checks that parsing an empty block raises no errors.
        """
        blocks = parse_filename(full_path('empty_block.manifest'))
        assert len(blocks) == 1
        fblock = blocks[0]
        assert isinstance(fblock, file_block.FileBlock)

    @istest
    def single_attr_block(self):
        """
        Integration: Parse File With Single Attr Block

        Checks that parsing a block with one attribute raises no errors.
        """
        blocks = parse_filename(full_path('single_attr.manifest'))
        assert len(blocks) == 1
        fblock = blocks[0]
        assert isinstance(fblock, file_block.FileBlock)
        assert fblock.get('source') == '/a/b/c'

    @istest
    def multiple_attr_block(self):
        """
        Integration: Parse File With Multiple Attr Block

        Checks that parsing a block with several attributes raises no
        errors.
        """
        blocks = parse_filename(full_path('two_attr.manifest'))
        assert len(blocks) == 1
        fblock = blocks[0]
        assert isinstance(fblock, file_block.FileBlock)
        assert fblock.get('source') == '/a/b/c'
        assert fblock.get('target') == '/d/e'

    @istest
    def spaced_attr_block(self):
        """
        Integration: Parse File With Block Attr Containing Spaces

        Checks that parsing a block with several attributes raises no
        errors.
        """
        blocks = parse_filename(full_path('spaced_attr.manifest'))
        assert len(blocks) == 1
        fblock = blocks[0]
        assert isinstance(fblock, file_block.FileBlock)
        assert fblock.get('source') == '/a/b/c'
        assert fblock.get('target') == '/d/e f/g'

    @istest
    def unclosed_block_raises_TE(self):
        """
        Integration: Parsing Unclosed Block Raises TokenizationException

        Not only validates that a TokenizationException occurs, but also
        verifies the context of the raised exception.
        """
        path = full_path('unclosed_block.manifest')
        e = ensure_except(tokenize.TokenizationException,
                          parse_filename,
                          path)
        sctx = e.file_context
        assert sctx.lineno == 4
        assert paths.clean_path(sctx.filename, absolute=True) == path

    @istest
    def missing_open_raises_TE(self):
        """
        Integration: Parsing Unopened Block Raises TokenizationException

        Not only validates that a TokenizationException occurs, but also
        verifies the context of the raised exception.
        """
        path = full_path('missing_open.manifest')
        e = ensure_except(tokenize.TokenizationException,
                          parse_filename,
                          path)
        sctx = e.file_context
        assert sctx.lineno == 5
        assert paths.clean_path(sctx.filename, absolute=True) == path

    @istest
    def missing_identifier_raises_TE(self):
        """
        Integration: Parsing Missing Block ID Raises TokenizationException

        Not only validates that a TokenizationException occurs, but also
        verifies the context of the raised exception.
        """
        path = full_path('missing_id.manifest')
        e = ensure_except(tokenize.TokenizationException,
                          parse_filename,
                          path)
        sctx = e.file_context
        assert sctx.lineno == 3
        assert paths.clean_path(sctx.filename, absolute=True) == path

    @istest
    def missing_value_raises_TE(self):
        """
        Integration: Parsing Missing Block ID Raises TokenizationException

        Not only validates that a TokenizationException occurs, but also
        verifies the context of the raised exception.
        """
        path = full_path('missing_attr_val.manifest')
        e = ensure_except(tokenize.TokenizationException,
                          parse_filename,
                          path)
        sctx = e.file_context
        assert sctx.lineno == 5
        assert paths.clean_path(sctx.filename, absolute=True) == path

    @istest
    def double_open_raises_TE(self):
        """
        Integration: Parsing Double Block Open Raises TokenizationException

        Not only validates that a TokenizationException occurs, but also
        verifies the context of the raised exception.
        """
        path = full_path('double_open.manifest')
        e = ensure_except(tokenize.TokenizationException,
                          parse_filename,
                          path)
        sctx = e.file_context
        assert sctx.lineno == 3
        assert paths.clean_path(sctx.filename, absolute=True) == path

    @istest
    def invalid_block_id_raises_PE(self):
        """
        Integration: Parse File With Invalid Block ID Raises ParsingException

        Not only validates that a TokenizationException occurs, but also
        verifies the context of the raised exception.
        """
        path = full_path('invalid_block_id.manifest')
        e = ensure_except(parse.ParsingException,
                          parse_filename,
                          path)
        sctx = e.file_context
        assert sctx.lineno == 7
        assert paths.clean_path(sctx.filename, absolute=True) == path
