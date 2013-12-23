#!/usr/bin/python

import string
import shlex

from src.util.enum import Enum
from src.util.error import SALVEException, StreamContext
from src.util.streams import get_filename

class TokenizationException(SALVEException):
    """
    A SALVE exception specialized for tokenization.
    """
    def __init__(self,msg,context):
        """
        TokenizationException constructor

        Args:
            @msg
            A string message that describes the error.
            @context
            A StreamContext that identifies the origin of this
            exception.
        """
        SALVEException.__init__(self,msg,context)

class Token(object):
    """
    A Token is an element of an input stream that has not had any
    parsing logic applied to it.

    Tokens are mildly sensitive to their context, and may raise errors
    if found in an invalid ordering.
    """
    # these are the valid token types
    types = Enum('IDENTIFIER','BLOCK_START','BLOCK_END','TEMPLATE')
    def __init__(self,value,ty,context):
        """
        Token constructor

        Args:
            @value
            The string contained in the Token, the original element of
            the input stream.
            @ty
            The type of this token. Determined from context and content.
            @context
            The StreamContext at which this Token was found.
        """
        self.value = value
        self.ty = ty
        self.context = context

    def __str__(self):
        """
        stringify a Token
        """
        attrs = ['value='+self.value,'ty='+self.ty,
                 'lineno='+str(self.context.lineno)]
        if self.context.filename:
            attrs.append('filename='+self.context.filename)
        return 'Token('+','.join(attrs)+')'

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
    def is_block_delim(token):
        """
        Check if a token is a BLOCK_START or BLOCK_END

        Args:
            @token
            Not a Token, but a raw string being examined.
        """
        return token == '{' or token == '}'

    def unexpected_token(token_str,expected,context):
        """
        Raise an exception due to an unexpected Token being fund in the
        input stream. Usually means that there are out of order tokens.

        Args:
            @token_str
            Not a Token, but a string that was found in the stream.
            @expected
            The expected type(s) of the Token.
            @context
            A StreamContext identifying this location in the file.
        """
        raise TokenizationException('Unexpected token: ' + token_str +\
            ' Expected ' + str(expected) + ' instead.',
            context)

    """
    State definitions
        FREE: Waiting for a block identifier
        IDENTIFIER_FOUND: Got a block identifier, waiting for a {
        BLOCK: Inside of a block, waiting for an attribute identifier
            or }
        IDENTIFIER_FOUND_BLOCK: Inside of a block, got an attribute
            identifier, waiting for a template string value
    """
    states = Enum('FREE', 'IDENTIFIER_FOUND', 'BLOCK',
                  'IDENTIFIER_FOUND_BLOCK')

    filename = get_filename(stream)

    tokens = []
    state = states.FREE

    tokenizer = shlex.shlex(stream,posix=True)
    # Basically, everything other than BLOCK_START or BLOCK_END
    # is okay here, we'll let the os library handle it later wrt
    # whether or not a path is valid
    tokenizer.wordchars = string.letters + string.digits + \
                          '_-+=^&@`/\|~$()[].,<>*?!%#'

    def add_token(tok,ty,context):
        """
        Add a token to the list in progress.

        Args:
            @tok
            The string that was tokenized.
            @ty
            The Token type of @tok
            @context
            The StreamContext where @tok was found.
        """
        tokens.append(Token(tok,ty,context))

    # The tokenizer acts as a state machine, reading tokens and making
    # state transitions based on the token values
    # get the first Maybe(Token)
    current = tokenizer.get_token()
    while current is not None:
        ctx = StreamContext(filename,tokenizer.lineno)
        # if we have not found a block, the expectation is that we will
        # find a block identifier as the first token
        if state is states.FREE:
            if is_block_delim(current):
                unexpected_token(current,Token.types.IDENTIFIER,ctx)
            add_token(current,Token.types.IDENTIFIER,ctx)
            state = states.IDENTIFIER_FOUND

        # if we have found a block identifier, the next token must be
        # a block start, '{'
        elif state is states.IDENTIFIER_FOUND:
            if current != '{':
                unexpected_token(current,Token.types.BLOCK_START,ctx)
            add_token(current,Token.types.BLOCK_START,ctx)
            state = states.BLOCK

        # if we are in a block, the next token is either a block end,
        # '}', or an attribute identifier
        elif state is states.BLOCK:
            if current == '{':
                unexpected_token(current,
                    [Token.types.BLOCK_END,Token.types.IDENTIFIER],ctx)
            elif current == '}':
                add_token(current,Token.types.BLOCK_END,ctx)
                state = states.FREE
            else:
                add_token(current,Token.types.IDENTIFIER,ctx)
                state = states.IDENTIFIER_FOUND_BLOCK

        # if we are in a block and have found an attribute identifier,
        # then the next token must be the template string for that
        # attribute's value
        elif state is states.IDENTIFIER_FOUND_BLOCK:
            if is_block_delim(current):
                unexpected_token(current,Token.types.TEMPLATE,ctx)
            add_token(current,Token.types.TEMPLATE,ctx)
            state = states.BLOCK

        # get the next Maybe(Token)
        current = tokenizer.get_token()

    if state is not states.FREE:
        raise TokenizationException('Tokenizer ended in state ' + \
                                     state,ctx)

    return tokens
