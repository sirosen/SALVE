from nose.tools import istest

from salve import paths
from salve.block import FileBlock
from salve.exceptions import ParsingException, TokenizationException
from salve.parser import parse

from tests.util import scratch, ensure_except, full_path


def parse_filename(filename):
    with open(filename) as f:
        return parse.parse_stream(f)


def assert_parsing_fails(name, lineno=None,
                         exception_type=TokenizationException):
    path = full_path(name)
    e = ensure_except(exception_type,
                      parse_filename,
                      path)
    sctx = e.file_context
    if lineno:
        assert sctx.lineno == lineno
    assert paths.clean_path(sctx.filename, absolute=True) == path

    return e


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
        assert isinstance(fblock, FileBlock)

    @istest
    def single_attr_block(self):
        """
        Integration: Parse File With Single Attr Block

        Checks that parsing a block with one attribute raises no errors.
        """
        blocks = parse_filename(full_path('single_attr.manifest'))
        assert len(blocks) == 1
        fblock = blocks[0]
        assert isinstance(fblock, FileBlock)
        assert fblock['source'] == '/a/b/c'

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
        assert isinstance(fblock, FileBlock)
        assert fblock['source'] == '/a/b/c'
        assert fblock['target'] == '/d/e'

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
        assert isinstance(fblock, FileBlock)
        assert fblock['source'] == '/a/b/c'
        assert fblock['target'] == '/d/e f/g'

    @istest
    def unclosed_block_raises_TE(self):
        """
        Integration: Parsing Unclosed Block Raises TokenizationException

        Not only validates that a TokenizationException occurs, but also
        verifies the context of the raised exception.
        """
        assert_parsing_fails('unclosed_block.manifest', lineno=4)

    @istest
    def missing_open_raises_TE(self):
        """
        Integration: Parsing Unopened Block Raises TokenizationException

        Not only validates that a TokenizationException occurs, but also
        verifies the context of the raised exception.
        """
        assert_parsing_fails('missing_open.manifest', lineno=5)

    @istest
    def missing_identifier_raises_TE(self):
        """
        Integration: Parsing Missing Block ID Raises TokenizationException

        Not only validates that a TokenizationException occurs, but also
        verifies the context of the raised exception.
        """
        assert_parsing_fails('missing_id.manifest', lineno=3)

    @istest
    def missing_value_raises_TE(self):
        """
        Integration: Parsing Missing Block ID Raises TokenizationException

        Not only validates that a TokenizationException occurs, but also
        verifies the context of the raised exception.
        """
        assert_parsing_fails(
            'missing_attr_val.manifest',
            lineno=5)

    @istest
    def double_open_raises_TE(self):
        """
        Integration: Parsing Double Block Open Raises TokenizationException

        Not only validates that a TokenizationException occurs, but also
        verifies the context of the raised exception.
        """
        assert_parsing_fails(
            'double_open.manifest',
            lineno=3)

    @istest
    def invalid_block_id_raises_PE(self):
        """
        Integration: Parse File With Invalid Block ID Raises ParsingException

        Not only validates that a TokenizationException occurs, but also
        verifies the context of the raised exception.
        """
        assert_parsing_fails(
            'invalid_block_id.manifest',
            lineno=7,
            exception_type=ParsingException)
