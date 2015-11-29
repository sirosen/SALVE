from nose.tools import istest, eq_, ok_
from nose_parameterized import parameterized, param
from tests.framework import (scratch, ensure_except, full_path,
                             first_param_docfunc)

from salve import paths
from salve.block import FileBlock
from salve.exceptions import ParsingException, TokenizationException
from salve.parser import parse


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
        eq_(sctx.lineno, lineno)
    eq_(paths.clean_path(sctx.filename, absolute=True), path)

    return e


class TestWithScratchContainer(scratch.ScratchContainer):
    @istest
    def empty_file(self):
        """
        Integration: Parse Empty Manifest File

        Checks that parsing an empty file produces an empty list of blocks.
        """
        blocks = parse_filename(full_path('empty.manifest'))
        eq_(len(blocks), 0)

    @istest
    def empty_block(self):
        """
        Integration: Parse File With Empty Block

        Checks that parsing an empty block raises no errors.
        """
        blocks = parse_filename(full_path('empty_block.manifest'))
        eq_(len(blocks), 1)
        fblock = blocks[0]
        ok_(isinstance(fblock, FileBlock))

    @parameterized.expand(
        [param('Integration: Parse File With Single Attr Block',
               'single_attr.manifest', source='/a/b/c'),
         param('Integration: Parse File With Multiple Attr Block',
               'two_attr.manifest', source='/a/b/c', target='/d/e'),
         param('Integration: Parse File With Block Attr Containing Spaces',
               'spaced_attr.manifest', source='/a/b/c', target='/d/e f/g')],
        testcase_func_doc=first_param_docfunc)
    @istest
    def parameterized_single_fileblock_parse_tests(self, description,
                                                   manifest_name, **kwargs):

        blocks = parse_filename(full_path(manifest_name))
        eq_(len(blocks), 1)
        fblock = blocks[0]
        ok_(isinstance(fblock, FileBlock))

        for k, v in kwargs.items():
            eq_(fblock[k], v)

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
