#!/usr/bin/python

from __future__ import print_function
from ..util.enum import Enum
from tokenize import Token, tokenize_stream

class ParsingException(ValueError):
    """
    A barebones specialized exception for parsing errors.
    """
    def __init__(self,value):
        self.value = value

class Block(object):
    """
    A block is the basic unit of configuration.
    Typically, blocks describe files, SALVE manifests, patches, etc
    """
    types = Enum('FILE','MANIFEST')
    def __init__(self,ty):
        self.block_type = ty
        self.attrs = {}

    def add_attribute(self,attribute_name,value):
        self.attrs[attribute_name] = value

class FileBlock(Block):
    """
    A file block describes an action performed on a file.
    This includes creation, deletion, and string append.
    """
    def __init__(self):
        Block.__init__(self,Block.types.FILE)

class ManifestBlock(Block):
    """
    A manifest block describes another manifest to be expanded and
    executed. It may also specify properties of that manifest's
    execution. For example, if a manifest's blocks can be executed
    in parallel, or if its execution is conditional on a file existing.
    """
    def __init__(self):
        Block.__init__(self,Block.types.MANIFEST)

def block_from_identifier(id_token):
    """
    Given an identifier, constructs a block of the appropriate
    type and returns it.
    Fails if the identifier is unknown, or the token given is
    not an identifier.
    """
    assert id_token.ty == Token.types.IDENTIFIER
    # maps valid identifiers to block constructors
    block_constructor_map = {
        'file': FileBlock,
        'manifest': ManifestBlock
    }
    val = id_token.value.lower()
    for key in block_constructor_map:
        if val == key:
            return block_constructor_map[key]()
    raise ParsingException('Unknown block identifier ' + val)

def parse_tokens(tokens):
    """
    Converts a token list to a block list.
    This is not entirely stateless, but unlike the tokenizer,
    there are no explicit states.
    """
    blocks = []
    def unexpected_token(token,expected_types):
        raise ParsingException('Invalid token in sequence. ' + \
                               'Expected a token of types ' + \
                               str(expected_types) + \
                               ' but got token ' + \
                               token.value + ' of type ' +
                               token.ty + ' instead.')
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
            current_block = block_from_identifier(token)
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
                current_block.add_attribute(current_attr,token.value)
                expected_token_types = [ Token.types.BLOCK_END,
                                         Token.types.IDENTIFIER ]
            # no else because token types must be valid, as per
            # the earlier check for valid token type
    # if the token list terminates and there is still a block in
    # progress, it means that the block was not teminated
    if current_block is not None:
        raise ParsingException('Incomplete block in token stream!')

    return blocks

def parse_stream(stream):
    """
    @stream is any file-like object that supports read() or readlines()
    Parsing a stream is just tokenizing it, and then handing those
    tokens to the parser.
    """
    return parse_tokens(tokenize_stream(stream))
