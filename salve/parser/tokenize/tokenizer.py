import string
import shlex

from .token import Token
from salve.exceptions import TokenizationException

import salve
from salve import Enum, paths
from salve.context import FileContext
from salve.util import stream_filename


class Tokenizer(object):
    def __init__(self, stream):
        self.tokens = []

        # setup the lexer
        self.stream = stream
        self.filename = paths.clean_path(stream_filename(stream),
                                         absolute=True)
        self.shlexer = shlex.shlex(stream, posix=True)
        # Basically, everything other than BLOCK_START or BLOCK_END
        # is okay here, we'll let the os library handle it later wrt
        # whether or not a path is valid
        self.shlexer.wordchars = (string.ascii_letters + string.digits +
                                  '_-+=^&@`/\|~$()[].,<>*?!%#')

        self.filectx = None

        """
        State definitions
            FREE: Waiting for a block identifier or EOF

            IDENTIFIER_FOUND: Got a block identifier, waiting for a { or
            primary attr (template string)

            PRIMARY_ATTR_FOUND: Found a primary block attr, next is either { or
            another identifier, or EOF

            BLOCK: Inside of a block, waiting for an attribute identifier
                or }

            IDENTIFIER_FOUND_BLOCK: Inside of a block, got an attribute
                identifier, waiting for a template string value
        """
        self.state = None
        self.states = Enum('FREE', 'IDENTIFIER_FOUND', 'PRIMARY_ATTR_FOUND',
                           'BLOCK', 'IDENTIFIER_FOUND_BLOCK')

        self.allowed_token_types = {
            self.states.FREE: Token.types.IDENTIFIER,
            self.states.IDENTIFIER_FOUND: [Token.types.BLOCK_START,
                                           Token.types.TEMPLATE],
            self.states.PRIMARY_ATTR_FOUND: Token.types.BLOCK_START,
            self.states.BLOCK: [Token.types.BLOCK_END, Token.types.IDENTIFIER],
            self.states.IDENTIFIER_FOUND_BLOCK: Token.types.TEMPLATE
        }

    def get_allowed_token_types(self):
        return self.allowed_token_types[self.state]

    def validate_end_state(self):
        """
        Verify that the tokenizer is exiting in a non-failure state.
        """
        # we can either be FREE (i.e. last saw a '}') or PRIMARY_ATTR_FOUND
        # (i.e. last saw a '<block_id> <attr_val>') at the end of the file
        if self.state not in (self.states.FREE,
                              self.states.PRIMARY_ATTR_FOUND):
            raise TokenizationException('Tokenizer ended in state ' +
                                        self.state, self.filectx)

    def add_token(self, tok, ty, target_state=None):
        """
        Add a token to the list in progress and transition to the desired state

        Args:
            @tok
            The string that was tokenized.
            @ty
            The Token type of @tok

        KWArgs:
            @target_state
            When truthy, a tokenization state to which the tokenizer should
            transition after adding the token.
        """
        self.tokens.append(Token(tok, ty, self.filectx))

        if target_state:
            self.state = target_state

    def reject_unexpected_delims(self, token_str):
        def _reject():
            raise TokenizationException(
                'Unexpected token: {0} Expected {1} instead.'
                .format(token_str, self.get_allowed_token_types()),
                self.filectx)

        if (Token.types.BLOCK_START not in self.get_allowed_token_types()
                and token_str == '{'):
            _reject()
        elif (Token.types.BLOCK_END not in self.get_allowed_token_types()
                and token_str == '}'):
            _reject()

    def add_delim_or_fallback(self, token_str, delim_state,
                              fallback_ty, fallback_state):
        (ty, state) = {
            '{': (Token.types.BLOCK_START, delim_state),
            '}': (Token.types.BLOCK_END, delim_state),
        }.get(token_str, (fallback_ty, fallback_state))
        self.add_token(token_str, ty, target_state=state)

    def process_token(self, token_str):
        self.filectx = FileContext(self.filename, self.shlexer.lineno)
        self.reject_unexpected_delims(token_str)

        # if we have not found a block, the expectation is that we will
        # find a block identifier as the first token
        if self.state is self.states.FREE:
            self.add_token(token_str, Token.types.IDENTIFIER,
                           self.states.IDENTIFIER_FOUND)

        # if we have found a block identifier, the next token must be
        # a block start, '{', or the primary attr
        elif self.state is self.states.IDENTIFIER_FOUND:
            self.add_delim_or_fallback(
                token_str, self.states.BLOCK, Token.types.TEMPLATE,
                self.states.PRIMARY_ATTR_FOUND)

        elif self.state is self.states.PRIMARY_ATTR_FOUND:
            self.add_delim_or_fallback(
                token_str, self.states.BLOCK, Token.types.IDENTIFIER,
                self.states.IDENTIFIER_FOUND)

        # if we are in a block, the next token is either a block end,
        # '}', or an attribute identifier
        elif self.state is self.states.BLOCK:
            self.add_delim_or_fallback(
                token_str, self.states.FREE, Token.types.IDENTIFIER,
                self.states.IDENTIFIER_FOUND_BLOCK)

        # if we are in a block and have found an attribute identifier,
        # then the next token must be the template string for that
        # attribute's value
        elif self.state is self.states.IDENTIFIER_FOUND_BLOCK:
            self.add_token(token_str, Token.types.TEMPLATE, self.states.BLOCK)

    def process_stream(self):
        # The tokenizer acts as a state machine, reading tokens and making
        # state transitions based on the token values
        # get the first Maybe(Token)
        current = self.shlexer.get_token()
        while current is not None:
            self.process_token(current)
            # get the next Maybe(Token)
            current = self.shlexer.get_token()

        self.validate_end_state()


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
    tokenizer = Tokenizer(stream)
    tokenizer.state = tokenizer.states.FREE

    salve.logger.info('Beginning Tokenization of "{0}"'
                      .format(tokenizer.filename))

    tokenizer.process_stream()

    salve.logger.info('Finished Tokenization of "{0}"'
                      .format(tokenizer.filename))

    return tokenizer.tokens
