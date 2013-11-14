#!/usr/bin/python

from src.reader.tokenize import Token

from src.block.base_block import BlockException
import src.block.file_block
import src.block.manifest_block

# maps valid identifiers to block constructors
identifier_map = {
    'file':src.block.file_block.FileBlock,
    'manifest':src.block.manifest_block.ManifestBlock
}

def block_from_identifier(id_token):
    """
    Given an identifier, constructs a block of the appropriate
    type and returns it.
    Fails if the identifier is unknown, or the token given is
    not an identifier.
    """
    if id_token.ty != Token.types.IDENTIFIER:
        raise BlockException('Unknown block identifier '+str(id_token))
    val = id_token.value.lower()
    try:
        return identifier_map[val]()
    except KeyError:
        raise ValueError('Unknown block identifier ' + val)
