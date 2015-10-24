import string
import shlex

import salve
from salve import paths, Enum
from salve.context import FileContext, ExecutionContext
from salve.exceptions import TokenizationException

from salve.util import stream_filename


class Token(object):
    """
    A Token is an element of an input stream that has not had any
    parsing logic applied to it.

    Tokens are mildly sensitive to their context, and may raise errors
    if found in an invalid ordering.
    """
    # these are the valid token types
    types = Enum('IDENTIFIER', 'BLOCK_START', 'BLOCK_END', 'TEMPLATE')

    def __init__(self, value, ty, file_context):
        """
        Token constructor

        Args:
            @value
            The string contained in the Token, the original element of
            the input stream.
            @ty
            The type of this token. Determined from context and content.
            @file_context
            The FileContext.
        """
        self.value = value
        self.ty = ty
        self.file_context = file_context

    def __str__(self):
        """
        stringify a Token
        """
        attrs = ['value=' + self.value, 'ty=' + self.ty,
                 'lineno=' + str(self.file_context.lineno)]
        if self.file_context.filename:
            attrs.append('filename=' + self.file_context.filename)
        return 'Token(' + ','.join(attrs) + ')'


"""
State definitions
    FREE: Waiting for a block identifier or EOF

    IDENTIFIER_FOUND: Got a block identifier, waiting for a { or primary
    attr (template string)

    PRIMARY_ATTR_FOUND: Found a primary block attr, next is either { or
    another identifier, or EOF

    BLOCK: Inside of a block, waiting for an attribute identifier
        or }

    IDENTIFIER_FOUND_BLOCK: Inside of a block, got an attribute
        identifier, waiting for a template string value
"""
tokenizing_states = Enum('FREE', 'IDENTIFIER_FOUND', 'PRIMARY_ATTR_FOUND',
                         'BLOCK', 'IDENTIFIER_FOUND_BLOCK')
state_map = {
    tokenizing_states.FREE: Token.types.IDENTIFIER,
    tokenizing_states.IDENTIFIER_FOUND: [Token.types.BLOCK_START,
                                         Token.types.TEMPLATE],
    tokenizing_states.PRIMARY_ATTR_FOUND: Token.types.BLOCK_START,
    tokenizing_states.BLOCK: [Token.types.BLOCK_END, Token.types.IDENTIFIER],
    tokenizing_states.IDENTIFIER_FOUND_BLOCK: Token.types.TEMPLATE
}


def add_token(tok, ty):
    """
    Add a token to the list in progress.

    Args:
        @tok
        The string that was tokenized.
        @ty
        The Token type of @tok
    """
    ExecutionContext()['tokenizing']['tokens'].append(
        Token(tok, ty, ExecutionContext()['tokenizing']['filectx']))


def validate_end_state():
    """
    Verify that the tokenizer is exiting in a non-failure state.
    """
    # we can either be FREE (i.e. last saw a '}') or PRIMARY_ATTR_FOUND (i.e.
    # last saw a '<block_id> <attr_val>') at the end of the file
    tokenizing_ctx = ExecutionContext()['tokenizing']
    state = tokenizing_ctx['state']
    if state not in (tokenizing_states.FREE,
                     tokenizing_states.PRIMARY_ATTR_FOUND):
        raise TokenizationException('Tokenizer ended in state ' +
                                    state, tokenizing_ctx['filectx'])


def process_token(token_str, shlexer):
    tokenizing_ctx = ExecutionContext()['tokenizing']

    def _reject_unexpected(reject_start=False, reject_end=False):
        def _reject():
            raise TokenizationException(
                'Unexpected token: ' + token_str +
                ' Expected ' + str(tokenizing_ctx['expected_types']) +
                ' instead.', tokenizing_ctx['filectx'])

        if reject_start and token_str == '{':
            _reject()
        elif reject_end and token_str == '}':
            _reject()

    def _add_token(ty, target_state):
        add_token(token_str, ty)
        tokenizing_ctx['state'] = target_state

    def _add_delim_or_fallback(delim_state, fallback_ty, fallback_state):
        if token_str == '{':
            _add_token(Token.types.BLOCK_START, delim_state)
        elif token_str == '}':
            _add_token(Token.types.BLOCK_END, delim_state)
        else:
            _add_token(fallback_ty, fallback_state)

    # generate a new FileContext
    ctx = FileContext(tokenizing_ctx['filename'], lineno=shlexer.lineno)
    tokenizing_ctx['filectx'] = ctx

    tokenizing_ctx['expected_types'] = state_map[tokenizing_ctx['state']]

    # if we have not found a block, the expectation is that we will
    # find a block identifier as the first token
    if tokenizing_ctx['state'] is tokenizing_states.FREE:
        _reject_unexpected(reject_start=True, reject_end=True)
        _add_token(Token.types.IDENTIFIER, tokenizing_states.IDENTIFIER_FOUND)

    # if we have found a block identifier, the next token must be
    # a block start, '{', or the primary attr
    elif tokenizing_ctx['state'] is tokenizing_states.IDENTIFIER_FOUND:
        _reject_unexpected(reject_end=True)
        _add_delim_or_fallback(tokenizing_states.BLOCK, Token.types.TEMPLATE,
                               tokenizing_states.PRIMARY_ATTR_FOUND)

    elif tokenizing_ctx['state'] is tokenizing_states.PRIMARY_ATTR_FOUND:
        _reject_unexpected(reject_end=True)
        _add_delim_or_fallback(tokenizing_states.BLOCK, Token.types.IDENTIFIER,
                               tokenizing_states.IDENTIFIER_FOUND)

    # if we are in a block, the next token is either a block end,
    # '}', or an attribute identifier
    elif tokenizing_ctx['state'] is tokenizing_states.BLOCK:
        _reject_unexpected(reject_start=True)
        _add_delim_or_fallback(tokenizing_states.FREE, Token.types.IDENTIFIER,
                               tokenizing_states.IDENTIFIER_FOUND_BLOCK)

    # if we are in a block and have found an attribute identifier,
    # then the next token must be the template string for that
    # attribute's value
    elif tokenizing_ctx['state'] is tokenizing_states.IDENTIFIER_FOUND_BLOCK:
        _reject_unexpected(reject_start=True, reject_end=True)
        _add_token(Token.types.TEMPLATE, tokenizing_states.BLOCK)


def tokenize_stream(stream):
    """
    Convert an input stream into a list of Tokens.

    Args:
        @stream is actually any file-like object that supports read() or
        readlines(). We need one of these attributes in order to hand
        the stream off to shlex for basic tokenization.
        In addition to the shlex tokenization, we do some basic
        validation that the token order is valid, and tag tokens with
        their types.
    """
    filename = paths.clean_path(stream_filename(stream), absolute=True)

    # use the exec context to store parsing state as a dict
    ExecutionContext()['tokenizing'] = {}
    tokenizing_ctx = ExecutionContext()['tokenizing']

    tokenizing_ctx['tokens'] = []
    tokenizing_ctx['state'] = tokenizing_states.FREE
    tokenizing_ctx['filename'] = filename
    tokenizing_ctx['expected_types'] = Token.types.IDENTIFIER

    salve.logger.info('Beginning Tokenization of \"%s\"' % filename)
    shlexer = shlex.shlex(stream, posix=True)
    # Basically, everything other than BLOCK_START or BLOCK_END
    # is okay here, we'll let the os library handle it later wrt
    # whether or not a path is valid
    shlexer.wordchars = (string.ascii_letters + string.digits +
                         '_-+=^&@`/\|~$()[].,<>*?!%#')

    # The tokenizer acts as a state machine, reading tokens and making
    # state transitions based on the token values
    # get the first Maybe(Token)
    current = shlexer.get_token()
    while current is not None:
        process_token(current, shlexer)
        # get the next Maybe(Token)
        current = shlexer.get_token()

    validate_end_state()

    salve.logger.info('Finished Tokenization of \"%s\"' % filename)

    return tokenizing_ctx['tokens']
