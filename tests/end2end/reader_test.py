#!/usr/bin/python

from nose.tools import istest
from os.path import dirname, join as pjoin

import src.block.file_block

import src.reader.tokenize
import src.reader.parse

import src.util.locations as locations

from src.util.context import SALVEContext, ExecutionContext
import tests.utils.scratch
from tests.utils.exceptions import ensure_except

_testfile_dir = pjoin(dirname(__file__), 'testfiles')
dummy_exec_context = ExecutionContext()
dummy_context = SALVEContext(exec_context=dummy_exec_context)


def parse_filename(filename):
    with open(filename) as f:
        return src.reader.parse.parse_stream(dummy_context, f)


def get_full_path(filename):
    return locations.clean_path(pjoin(_testfile_dir, filename))


class TestWithScratchContainer(tests.utils.scratch.ScratchContainer):
    @istest
    def empty_file(self):
        """
        E2E: Parse Empty Manifest File

        Checks that parsing an empty file produces an empty list of blocks.
        """
        blocks = parse_filename(get_full_path('empty.manifest'))
        assert len(blocks) == 0

    @istest
    def empty_block(self):
        """
        E2E: Parse File With Empty Block

        Checks that parsing an empty block raises no errors.
        """
        blocks = parse_filename(get_full_path('empty_block.manifest'))
        assert len(blocks) == 1
        fblock = blocks[0]
        assert isinstance(fblock, src.block.file_block.FileBlock)

    @istest
    def single_attr_block(self):
        """
        E2E: Parse File With Single Attr Block

        Checks that parsing a block with one attribute raises no errors.
        """
        blocks = parse_filename(get_full_path('single_attr.manifest'))
        assert len(blocks) == 1
        fblock = blocks[0]
        assert isinstance(fblock, src.block.file_block.FileBlock)
        assert fblock.get('source') == '/a/b/c'

    @istest
    def multiple_attr_block(self):
        """
        E2E: Parse File With Multiple Attr Block

        Checks that parsing a block with several attributes raises no
        errors.
        """
        blocks = parse_filename(get_full_path('two_attr.manifest'))
        assert len(blocks) == 1
        fblock = blocks[0]
        assert isinstance(fblock, src.block.file_block.FileBlock)
        assert fblock.get('source') == '/a/b/c'
        assert fblock.get('target') == '/d/e'

    @istest
    def spaced_attr_block(self):
        """
        E2E: Parse File With Block Attr Containing Spaces

        Checks that parsing a block with several attributes raises no
        errors.
        """
        blocks = parse_filename(get_full_path('spaced_attr.manifest'))
        assert len(blocks) == 1
        fblock = blocks[0]
        assert isinstance(fblock, src.block.file_block.FileBlock)
        assert fblock.get('source') == '/a/b/c'
        assert fblock.get('target') == '/d/e f/g'

    @istest
    def unclosed_block_raises_TE(self):
        """
        E2E: Parse File With Unclosed Block Raises Tokenization Exception

        Not only validates that a Tokenization Exception occurs, but also
        verifies the context of the raised exception.
        """
        path = get_full_path('unclosed_block.manifest')
        e = ensure_except(src.reader.tokenize.TokenizationException,
                          parse_filename,
                          path)
        sctx = e.context.stream_context
        assert sctx.lineno == 4
        assert sctx.filename == path

    @istest
    def missing_open_raises_TE(self):
        """
        E2E: Parse File With Unopened Block Raises Tokenization Exception

        Not only validates that a Tokenization Exception occurs, but also
        verifies the context of the raised exception.
        """
        path = get_full_path('missing_open.manifest')
        e = ensure_except(src.reader.tokenize.TokenizationException,
                          parse_filename,
                          path)
        sctx = e.context.stream_context
        assert sctx.lineno == 5
        assert sctx.filename == path

    @istest
    def double_identifier_raises_TE(self):
        """
        E2E: Parse File With Repeated Block ID Raises Tokenization Exception

        Not only validates that a Tokenization Exception occurs, but also
        verifies the context of the raised exception.
        """
        path = get_full_path('double_id.manifest')
        e = ensure_except(src.reader.tokenize.TokenizationException,
                          parse_filename,
                          path)
        sctx = e.context.stream_context
        assert sctx.lineno == 5
        assert sctx.filename == path

    @istest
    def missing_identifier_raises_TE(self):
        """
        E2E: Parse File With Missing Block ID Raises Tokenization Exception

        Not only validates that a Tokenization Exception occurs, but also
        verifies the context of the raised exception.
        """
        path = get_full_path('missing_id.manifest')
        e = ensure_except(src.reader.tokenize.TokenizationException,
                          parse_filename,
                          path)
        sctx = e.context.stream_context
        assert sctx.lineno == 3
        assert sctx.filename == path

    @istest
    def missing_value_raises_TE(self):
        """
        E2E: Parse File With Missing Block ID Raises Tokenization Exception

        Not only validates that a Tokenization Exception occurs, but also
        verifies the context of the raised exception.
        """
        path = get_full_path('missing_attr_val.manifest')
        e = ensure_except(src.reader.tokenize.TokenizationException,
                          parse_filename,
                          path)
        sctx = e.context.stream_context
        assert sctx.lineno == 5
        assert sctx.filename == path

    @istest
    def double_open_raises_TE(self):
        """
        E2E: Parse File With Double Block Open Raises Tokenization Exception

        Not only validates that a Tokenization Exception occurs, but also
        verifies the context of the raised exception.
        """
        path = get_full_path('double_open.manifest')
        e = ensure_except(src.reader.tokenize.TokenizationException,
                          parse_filename,
                          path)
        sctx = e.context.stream_context
        assert sctx.lineno == 3
        assert sctx.filename == path

    @istest
    def invalid_block_id_raises_PE(self):
        """
        E2E: Parse File With Invalid Block ID Raises Parsing Exception

        Not only validates that a Tokenization Exception occurs, but also
        verifies the context of the raised exception.
        """
        path = get_full_path('invalid_block_id.manifest')
        e = ensure_except(src.reader.parse.ParsingException,
                          parse_filename,
                          path)
        sctx = e.context.stream_context
        assert sctx.lineno == 7
        assert sctx.filename == path
