from nose.tools import istest

from salve import paths
from salve.context import FileContext
from salve.parser import tokenize
from salve.parser.tokenize import Token

from tests.util import ensure_except, full_path, MockedGlobals


def tokenize_filename(filename):
    with open(filename) as f:
        return tokenize.tokenize_stream(f)


def ensure_TokenizationException(filename):
    path = full_path(filename)
    e = ensure_except(tokenize.TokenizationException,
                      tokenize_filename,
                      path)
    assert (paths.clean_path(e.file_context.filename) ==
            paths.clean_path(path))


def assert_tokens_match_types(tokens, types):
    assert len(tokens) == len(types)

    for (tok, ty) in zip(tokens, types):
        assert tok.ty == ty


# useful lists for piecing together expected series of tokens
empty_block_tys = [Token.types.BLOCK_START, Token.types.BLOCK_END]
id_and_empty_block_tys = [Token.types.IDENTIFIER] + empty_block_tys
id_and_start_tys = [Token.types.IDENTIFIER, Token.types.BLOCK_START]
id_and_template_tys = [Token.types.IDENTIFIER, Token.types.TEMPLATE]


class TestTokenizeMockedGlobals(MockedGlobals):
    @istest
    def unclosed_block(self):
        """
        Unit: Tokenizer Unclosed Block Fails
        Ensures that an unclosed block raises a TokenizationException.
        """
        ensure_TokenizationException('unclosed_block.manifest')

    @istest
    def missing_open(self):
        """
        Unit: Tokenizer Missing Block Open Fails
        Ensures that a missing { raises a TokenizationException.
        """
        ensure_TokenizationException('missing_open.manifest')

    @istest
    def missing_open_primary_attr(self):
        """
        Unit: Tokenizer Missing Block Open (Primary Attribute Block) Fails
        Ensures that a missing { raises a TokenizationException even on block's
        with a Primary Attribute setting.
        """
        ensure_TokenizationException('primary_attr_block_close.manifest')

    @istest
    def missing_block_identifier(self):
        """
        Unit: Tokenizer Missing Identifier Fails
        Ensures that a missing block id raises a TokenizationException.
        """
        ensure_TokenizationException('missing_id.manifest')

    @istest
    def missing_attribute_value(self):
        """
        Unit: Tokenizer Missing Attribute Value Fails
        Ensures that a block attribute without a value raises a
        TokenizationException.
        """
        ensure_TokenizationException('missing_attr_val.manifest')

    @istest
    def bare_identifier(self):
        """
        Unit: Tokenizer Bare Identifier Fails
        Ensures that a block without body or primary attr value raises a
        TokenizationException.
        """
        ensure_TokenizationException('bare_id.manifest')

    @istest
    def double_open(self):
        """
        Unit: Tokenizer Double Open Fails
        Ensures that repeated '{'s raise a TokenizationException.
        """
        ensure_TokenizationException('double_open.manifest')

    # validation tests

    @istest
    def empty_manifest(self):
        """
        Unit: Tokenizer Empty Manifest
        Verifies that tokenizing an empty file produces an empty token list.
        """
        tokens = tokenize_filename(full_path('empty.manifest'))
        assert len(tokens) == 0

    @istest
    def empty_block(self):
        """
        Unit: Tokenizer Empty Block
        Verifies that tokenizing an empty block produces a token list
        containing the identifier, a block open, and a block close.
        """
        tokens = tokenize_filename(full_path('empty_block.manifest'))
        assert_tokens_match_types(tokens, id_and_empty_block_tys)

    @istest
    def invalid_id_nofail(self):
        """
        Unit: Tokenizer Invalid Identifier (No Fail)
        Ensures that no exception is raised if the tokenizer encounters an
        unknown block identifier.
        """
        tokens = tokenize_filename(full_path('invalid_block_id.manifest'))
        assert_tokens_match_types(
            tokens,
            id_and_start_tys + id_and_template_tys +
            [Token.types.BLOCK_END] + id_and_empty_block_tys
        )

    @istest
    def attribute_with_spaces(self):
        """
        Unit: Tokenizer Attribute With Spaces
        Verifies that tokenization proceeds correctly when an attribute
        value is a quoted string containing spaces.
        """
        tokens = tokenize_filename(full_path('spaced_attr.manifest'))
        assert_tokens_match_types(
            tokens,
            id_and_start_tys + 2*id_and_template_tys + [Token.types.BLOCK_END]
        )

    @istest
    def primary_attr_block_followed_by_block(self):
        """
        Unit: Tokenizer Primary Attribute Block Followed By Normal Block
        Verifies that tokenization proceeds correctly when a "Primary
        Attribute" style block is followed by an ordinary block.
        """
        tokens = tokenize_filename(full_path('primary_attr2.manifest'))
        assert_tokens_match_types(
            tokens,
            id_and_template_tys + id_and_start_tys +
            2*id_and_template_tys + [Token.types.BLOCK_END]
        )

    @istest
    def primary_attr_block_series(self):
        """
        Unit: Tokenizer Multiple Primary Attribute Blocks
        Verifies that tokenization proceeds correctly when a group of "Primary
        Attribute" style blocks are given in series
        """
        tokens = tokenize_filename(full_path('primary_attr3.manifest'))
        assert_tokens_match_types(tokens, 4*id_and_template_tys)

    @istest
    def primary_attr_block_empty_body(self):
        """
        Unit: Tokenizer Primary Attribute Block Empty Body
        Verifies that tokenization proceeds correctly when a "Primary
        Attribute" style block is given a "{}" body
        """
        tokens = tokenize_filename(full_path('primary_attr4.manifest'))
        assert_tokens_match_types(tokens,
                                  id_and_template_tys + empty_block_tys)

    @istest
    def token_to_string(self):
        """
        Unit: Tokenizer Token To String
        Checks the result of invoking Token.__str__
        """
        ctx = FileContext('a/b/c', 2)
        file_tok = Token('file', Token.types.IDENTIFIER, ctx)
        assert (str(file_tok) ==
                'Token(value=file,ty=IDENTIFIER,lineno=2,filename=a/b/c)')
