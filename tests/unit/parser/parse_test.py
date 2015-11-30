from nose.tools import istest, eq_, ok_
from nose_parameterized import parameterized, param
from tests.framework import (ensure_except, full_path, MockedGlobals,
                             first_param_docfunc)

from salve import paths
from salve.parser import parse, Token
from salve.context import FileContext
from salve.block import FileBlock, ManifestBlock

dummy_context = FileContext('no such file')


def parse_filename(filename):
    with open(filename) as f:
        return parse.parse_stream(f)


def ensure_ParsingException(tokens=None, filename=None):
    if tokens and filename:
        raise ValueError('Invalid test: uses both tokens list and '
                         'filename in ensure_ParsingException()')
    elif not tokens and not filename:
        raise ValueError('Invalid test: uses neither tokens list nor '
                         'filename in ensure_ParsingException()')

    if tokens:
        method, target = parse.parse_tokens, tokens
    else:
        method, target = parse_filename, full_path(filename)
    e = ensure_except(parse.ParsingException, method, target)

    if filename:
        eq_(paths.clean_path(e.file_context.filename),
            paths.clean_path(full_path(filename)))


def _generate_tokens(*args):
    return [Token(name, ty, dummy_context) for (name, ty) in args]


def _check_blocks(block_list, *args):
    eq_(len(block_list), len(args))

    for (i, (ty, num_attrs)) in enumerate(args):
        ok_(isinstance(block_list[i], ty))
        eq_(len(block_list[i].attrs), num_attrs)


basic_filecheck_params = [
    param('Unit: Parser Empty File', 'empty.manifest'),
    param('Unit: Parser Empty Block In File', 'empty_block.manifest',
          (FileBlock, 0)),
    param('Unit: Parser Attribute With Spaces', 'spaced_attr.manifest',
          (FileBlock, 2)),
]


parse_exception_token_params = [
    param('Unit: Parser Invalid Block Identifier From File',
          ('invalid_block_id', Token.types.IDENTIFIER)),
    param('Unit: Parser Unexpected Token', ('{', Token.types.BLOCK_START)),
    param('Unit: Parser Partial Block Fails (No Open)',
          ('file', Token.types.IDENTIFIER)),
    param('Unit: Parser Partial Block Fails (No Close)',
          ('file', Token.types.IDENTIFIER), ('{', Token.types.BLOCK_START)),
    param('Unit: Parser Unassigned Attribute Fails',
          ('file', Token.types.IDENTIFIER), ('{', Token.types.BLOCK_START),
          ('source', Token.types.IDENTIFIER), ('}', Token.types.BLOCK_END)),
]


parse_exception_file_params = [
    param('Unit: Parser Invalid Block Identifier',
          'invalid_block_id.manifest'),
]


class TestParsingMockedGlobals(MockedGlobals):
    @parameterized.expand(parse_exception_token_params,
                          testcase_func_doc=first_param_docfunc)
    @istest
    def invalid_token_set(self, description, *args):
        ensure_ParsingException(tokens=_generate_tokens(*args))

    @parameterized.expand(parse_exception_file_params,
                          testcase_func_doc=first_param_docfunc)
    @istest
    def invalid_file(self, description, filename):
        ensure_ParsingException(filename=filename)

    @istest
    def empty_token_list(self):
        """
        Unit: Parser Empty Token List
        Checks that parsing an empty token list produces an empty list of
        blocks.
        """
        eq_(len(parse.parse_tokens([])), 0)

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
        eq_(blocks[0]['source'], '/tmp/txt')

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
        eq_(blocks[0]['source'], '/tmp/txt')
        eq_(blocks[0]['target'], '/tmp/txt2')

    @parameterized.expand(basic_filecheck_params,
                          testcase_func_doc=first_param_docfunc)
    @istest
    def basic_fileparse_checks(self, description, filename, *args):
        _check_blocks(parse_filename(full_path(filename)), *args)

    @istest
    def file_primary_attr_assigned(self):
        """
        Unit: Parser File Block Primary Attr
        Checks that parsing a Primary Attribute style file block does not raise
        any errors.
        """
        blocks = parse_filename(full_path('primary_attr.manifest'))
        _check_blocks(blocks, (FileBlock, 2))
        eq_(blocks[0][blocks[0].primary_attr], "/d/e/f/g")

    @istest
    def primary_attr_followed_by_block(self):
        """
        Unit: Parser Primary Attribute Block Followed By Normal Block
        Checks that there are no errors parsing a Primary Attribute style block
        followed by an ordinary block.
        """
        blocks = parse_filename(full_path('primary_attr2.manifest'))
        _check_blocks(blocks, (ManifestBlock, 1), (FileBlock, 2))
        eq_(blocks[0][blocks[0].primary_attr], "man man")
        eq_(blocks[1]['source'], "potato")
        eq_(blocks[1]['target'], "mango")

    @istest
    def file_primary_attr_with_body(self):
        """
        Unit: Parser File Block Primary Attr And Block Body
        Checks that parsing is successful on a primary attr block with a
        nonempty body.
        """
        blocks = parse_filename(full_path('primary_attr5.manifest'))
        _check_blocks(blocks, (FileBlock, 2))
        eq_(blocks[0][blocks[0].primary_attr], "lobster")
        eq_(blocks[0]['source'], "salad")
