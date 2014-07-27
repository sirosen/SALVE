#!/usr/bin/python

import salve

import salve.block.identifier
from salve.util.streams import get_filename
from salve.util.error import SALVEException
from salve.reader.tokenize import Token, tokenize_stream


class ParsingException(SALVEException):
    """
    A specialized exception for parsing errors.

    A ParsingException (PE) often carres the token that tripped the
    exception in its message.
    """
    def __init__(self, msg, file_context):
        """
        ParsingException constructor

        Args:
            @msg
            A string message that describes the error.
            @file_context
            The FileContext.
        """
        SALVEException.__init__(self, msg, file_context)


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
    salve.logger.info('Beginning Parse of Token Stream', min_verbosity=2)

    blocks = []

    def unexpected_token(token, expected_types):
        raise ParsingException('Invalid token.' +
            'Expected a token of types ' + str(expected_types) +
            ' but got token ' + token.value + ' of type ' + token.ty +
            ' instead.', token.file_context)

    # track the expected next token(s)
    expected_token_types = [Token.types.IDENTIFIER]
    # tracks whether or not parsing is inside of a "{" "}" delimited block
    in_block = False

    # the current_block and current_attr are used to build blocks
    # before they are appended to the blocks list
    current_block = None
    current_attr = None

    for token in tokens:
        # if the token is unexpected, throw an exception and fail
        if token.ty not in expected_token_types:
            unexpected_token(token, expected_token_types)

        # if the token is an identifier found outside of a block, it is the
        # beginning of a new block
        elif not in_block and token.ty == Token.types.IDENTIFIER:
            try:
                b_from_id = salve.block.identifier.block_from_identifier
                current_block = b_from_id(token)
                blocks.append(current_block)
            except:
                raise ParsingException('Invalid block id ' +
                    token.value, token.file_context)
            expected_token_types = [Token.types.BLOCK_START,
                                    Token.types.TEMPLATE]

        else:
            # if the token is a block start, set in_block
            if token.ty == Token.types.BLOCK_START:
                in_block = True
                expected_token_types = [Token.types.BLOCK_END,
                                        Token.types.IDENTIFIER]
            # if the token is a block end, add the current block to the
            # list and set current_block to None
            elif token.ty == Token.types.BLOCK_END:
                in_block = False
                expected_token_types = [Token.types.IDENTIFIER]

            # if the token is an identifier, it is the name of an attr (because
            # we've already checked to see
            elif token.ty == Token.types.IDENTIFIER:
                current_attr = token.value.lower()
                expected_token_types = [Token.types.TEMPLATE]

            # if the token is a template string, assign it to the
            # current attr
            elif token.ty == Token.types.TEMPLATE:
                # primary_attr is being assigned
                if current_attr is None:
                    current_attr = current_block.primary_attr
                    expected_token_types = [Token.types.BLOCK_START,
                                            Token.types.IDENTIFIER]
                # non-primary attr is being assigned (ordinary block attr)
                else:
                    expected_token_types = [Token.types.BLOCK_END,
                                            Token.types.IDENTIFIER]
                current_block.set(current_attr, token.value)
                current_attr = None

            # no meaningful else because token types must be valid, as
            # per the earlier check for valid token type
            else:
                raise ValueError('SALVE Internal Error!')  # pragma: no cover

    # if the token list terminates and there is still a block in
    # progress or a TEMPLATE could come next, it means that the block was not
    # teminated properly
    if in_block or Token.types.TEMPLATE in expected_token_types:
        # this PE carries no token because it is the absence of a token
        # that triggers it
        raise ParsingException('Incomplete block in token stream!',
            current_block.file_context)

    salve.logger.info('Finished Parsing Token Stream', min_verbosity=2)

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
