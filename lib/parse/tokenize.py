#!/usr/bin/python

from __future__ import print_function
import string, shlex
from ..util.enum import Enum

_token_types = Enum('IDENTIFIER', 'BLOCK_START'='{', 'BLOCK_END'='}',
                   'TEMPLATE_STRING')

class TokenizationException(ValueError):
    def __init__(self,value):
        self.value = value

class Token(object):
    def __init__(self,value,token_type):
        self.value = value
        self.token_type = token_type

def _is_block_delim(token):
    return token == _token_types.BLOCK_START or \
           token == _token_types.BLOCK_END

def _raise_unexpected_token(token,expected):
    raise TokenizationException('Expected a ' + expected +
            ' token, but found "' + token + '" instead!')

# @stream is actually any file-like object that supports basic
# line-by-line iteration
def main(stream):
    tokens = []
    valid_identifier_chars = string.letters+string.digits+'_-'
    states = Enum('NO_BLOCK', 'IDENTIFIER_FOUND_NO_BLOCK',
                  'BLOCK', 'IDENTIFIER_FOUND_BLOCK')
    state = states.NO_BLOCK

    tokenizer = shlex.shlex(stream,comments=True)
    # Basically, everything other than BLOCK_START or BLOCK_END
    # is okay here, we'll let the os library handle it later
    tokenizer.wordchars = string.letters+string.digits +
                          '_-+=^&@`/\|~$()[].,<>*?!%#'

    current = tokenizer.get_token()
    while current is not None:
        if state == states.NO_BLOCK:
            if _is_block_delim(current):
                _raise_unexpected_token(current,'IDENTIFIER')
            tokens.append(Token(current,_token_types.IDENTIFIER))
            state = states.IDENTIFIER_FOUND_NO_BLOCK
        elif state == states.IDENTIFIER_FOUND_NO_BLOCK:
            if current != _token_types.BLOCK_START:
                _raise_unexpected_token(current,'BLOCK_START')
            tokens.append(Token(current,_token_types.BLOCK_START))
        elif state == states.BLOCK:
            if current == _token_types.BLOCK_START:
                _raise_unexpected_token(current,
                                        'IDENTIFIER or BLOCK_END')
            elif current == _token_types.BLOCK_END:
                tokens.append(Token(current,_token_types.BLOCK_END))
                state = states.NO_BLOCK
            else:
                tokens.append(Token(current,_token_types.IDENTIFIER))
                state = states.IDENTIFIER_FOUND_BLOCK
        elif state == states.IDENTIFIER_FOUND_BLOCK:
            if _is_block_delim(current):
                _raise_unexpected_token(current,'TEMPLATE_STRING')
            tokens.append(Token(current,_token_types.TEMPLATE_STRING))
        current = tokenizer.get_token()
