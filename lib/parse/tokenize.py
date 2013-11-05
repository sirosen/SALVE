#!/usr/bin/python

from __future__ import print_function
import string, shlex
from ..util.enum import Enum

class TokenizationException(ValueError):
    def __init__(self,value):
        self.value = value

class Token(object):
    types = Enum('IDENTIFIER','BLOCK_START','BLOCK_END','TEMPLATE')
    def __init__(self,value,ty):
        self.value = value
        self.ty = ty

def tokenize_stream(stream):
    """
    @stream is actually any file-like object that supports read() or
    readlines(). We need one of these attributes in order to hand the
    stream off to shlex for basic tokenization.
    In addition to the shlex tokenization, we do some basic validation
    that the token order is valid, and tag tokens with their types.
    Produces a Token list.
    """
    def is_block_delim(token):
        return token == '{' or token == '}'

    def unexpected_token(token,expected):
        raise TokenizationException('Expected a ' + expected +
                ' token, but found "' + token + '" instead!')

    states = Enum('FREE', 'IDENTIFIER_FOUND', 'BLOCK',
                  'IDENTIFIER_FOUND_BLOCK')

    tokens = []
    state = states.FREE

    tokenizer = shlex.shlex(stream,posix=True)
    # Basically, everything other than BLOCK_START or BLOCK_END
    # is okay here, we'll let the os library handle it later wrt
    # whether or not a path is valid
    tokenizer.wordchars = string.letters + string.digits + \
                          '_-+=^&@`/\|~$()[].,<>*?!%#'

    # The tokenizer acts as a state machine, reading tokens and making
    # state transitions based on the token values
    # get the first Maybe(Token)
    current = tokenizer.get_token()
    while current is not None:
        # if we have not found a block, the expectation is that we will
        # find a block identifier as the first token
        if state is states.FREE:
            if is_block_delim(current):
                unexpected_token(current,Token.types.IDENTIFIER)
            tokens.append(Token(current,Token.types.IDENTIFIER))
            state = states.IDENTIFIER_FOUND

        # if we have found a block identifier, the next token must be
        # a block start, '{'
        elif state is states.IDENTIFIER_FOUND:
            if current != '{':
                unexpected_token(current,'BLOCK_START')
            tokens.append(Token(current,Token.types.BLOCK_START))
            state = states.BLOCK

        # if we are in a block, the next token is either a block end,
        # '}', or an attribute identifier
        elif state is states.BLOCK:
            if current == '{':
                unexpected_token(current, 'IDENTIFIER or BLOCK_END')
            elif current == '}':
                tokens.append(Token(current,Token.types.BLOCK_END))
                state = states.FREE
            else:
                tokens.append(Token(current,Token.types.IDENTIFIER))
                state = states.IDENTIFIER_FOUND_BLOCK

        # if we are in a block and have found an attribute identifier,
        # then the next token must be the template string for that
        # attribute's value
        elif state is states.IDENTIFIER_FOUND_BLOCK:
            if is_block_delim(current):
                unexpected_token(current,'TEMPLATE')
            tokens.append(Token(current,Token.types.TEMPLATE))
            state = states.BLOCK

        # get the next Maybe(Token)
        current = tokenizer.get_token()

    if state is not states.FREE:
        raise TokenizationException('Tokenizer ended in state ' + \
                                     state)

    return tokens
