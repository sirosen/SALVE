#!/usr/bin/python

import src.block.identifier
from src.util.streams import get_filename
from src.util.error import SALVEException, StreamContext
from src.reader.tokenize import Token, tokenize_stream

class ParsingException(SALVEException):
    """
    A specialized exception for parsing errors.

    A ParsingException (PE) often carres the token that tripped the
    exception in its message.
    """
    def __init__(self,msg,context):
        """
        ParsingException constructor

        Args:
            @msg
            A string message that describes the error.
            @context
            A StreamContext that identifies the origin of this
            exception.
        """
        SALVEException.__init__(self,msg,context)

def parse_tokens(tokens):
    """
    Converts a token list to a block list.
    This is not entirely stateless, but unlike the tokenizer,
    there are no explicit states.

    Args:
        @tokens
        An iterable (generally a list) of Tokens to parse into Blocks.
        Unordered iterables won't work here, as parsing is very
        sensitive to token ordering.
    """
    blocks = []
    def unexpected_token(token,expected_types):
        raise ParsingException('Invalid token.' +\
            'Expected a token of types ' + str(expected_types) +\
            ' but got token ' + token.value + ' of type ' + token.ty +\
            ' instead.',token.context)

    # track the expected next token(s)
    expected_token_types = [ Token.types.IDENTIFIER ]
    # the current_block and current_attr are used to build blocks
    # before they are appended to the blocks list
    current_block = None
    current_attr = None
    for token in tokens:
        # if the token is unexpected, throw an exception and fail
        if token.ty not in expected_token_types:
            unexpected_token(token,expected_token_types)
        # if there is no current block, the incoming token must
        # be an identifier, so we can use it to construct a new block
        elif not current_block:
            try:
                b_from_id = src.block.identifier.block_from_identifier
                current_block = b_from_id(token)
            except:
                raise ParsingException('Invalid block id ' +\
                    token.value,token.context)
            expected_token_types = [ Token.types.BLOCK_START ]
        else:
            # if the token is a block start, do nothing
            if token.ty == Token.types.BLOCK_START:
                expected_token_types = [ Token.types.BLOCK_END,
                                         Token.types.IDENTIFIER ]
            # if the token is a block end, add the current block to the
            # list and set current_block to None
            elif token.ty == Token.types.BLOCK_END:
                blocks.append(current_block)
                current_block = None
                expected_token_types = [ Token.types.IDENTIFIER ]
            # if the token is an identifier, it is the name of an attr
            elif token.ty == Token.types.IDENTIFIER:
                current_attr = token.value.lower()
                expected_token_types = [ Token.types.TEMPLATE ]
            # if the token is a template string, assign it to the
            # current attr
            elif token.ty == Token.types.TEMPLATE:
                current_block.set(current_attr,token.value)
                expected_token_types = [ Token.types.BLOCK_END,
                                         Token.types.IDENTIFIER ]
            # no meaningful else because token types must be valid, as
            # per the earlier check for valid token type
            else: raise ValueError('SALVE Internal Error!') #pragma: no cover
    # if the token list terminates and there is still a block in
    # progress, it means that the block was not teminated
    if current_block is not None:
        # this PE carries no token because it is the absence of a token
        # that triggers it
        raise ParsingException('Incomplete block in token stream!',
            current_block.context)

    return blocks

def parse_stream(stream):
    """
    Parse a stream or file object into blocks.

    Args:
        @stream
        any file-like object that supports read() or readlines()
        Parsing a stream is just tokenizing it, and then handing those
        tokens to the parser.
    """
    return parse_tokens(tokenize_stream(stream))
