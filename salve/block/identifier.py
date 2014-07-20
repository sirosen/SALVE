#!/usr/bin/python

import salve

from salve.reader.tokenize import Token

from salve.block.base import BlockException
import salve.block.file_block
import salve.block.manifest_block
import salve.block.directory_block

from salve.util.context import SALVEContext

# maps valid identifiers to block constructors
identifier_map = {
    'file': salve.block.file_block.FileBlock,
    'manifest': salve.block.manifest_block.ManifestBlock,
    'directory': salve.block.directory_block.DirBlock
}


def block_from_identifier(context, id_token):
    """
    Given an identifier, constructs a block of the appropriate
    type and returns it.
    Fails if the identifier is unknown, or the token given is
    not an identifier.

    Args:
        @id_token
        The Token which is a block identifier. Consists of a string and
        little else.
    """
    # assert failures indicate an internal error (invalid state)
    assert isinstance(id_token, Token)
    if id_token.ty != Token.types.IDENTIFIER:
        raise BlockException('Cannot create block from non-identifier: ' +
                             str(id_token),
                             id_token.context.stream_context)

    salve.logger.info('Generating Block From Identifier Token: ' +
            str(id_token), file_context=id_token.context.stream_context,
            min_verbosity=3)

    # if the identifier is not in the map, raise an exception
    val = id_token.value.lower()
    ctx = SALVEContext(exec_context=context.exec_context,
                       stream_context=id_token.context.stream_context)
    try:
        return identifier_map[val](ctx)
    except KeyError:
        raise BlockException('Unknown block identifier ' + val, ctx)
    except:  # pragma: no cover
        raise  # pragma: no cover
