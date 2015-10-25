import salve

from salve.exceptions import BlockException
from salve.block.file import FileBlock
from salve.block.directory import DirBlock
from salve.block.manifest import ManifestBlock

# maps valid identifiers to block constructors
identifier_map = {
    'file': FileBlock,
    'manifest': ManifestBlock,
    'directory': DirBlock
}


def block_from_identifier(id_token):
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
    # import Token here to avoid circular dependency issues
    # the parser needs to know about the valid identifiers from here, but this
    # needs to know about Tokens
    from salve.parser import Token

    # assert failures indicate an internal error (invalid state)
    assert isinstance(id_token, Token)
    ctx = id_token.file_context
    if id_token.ty != Token.types.IDENTIFIER:
        raise BlockException('Cannot create block from non-identifier: ' +
                             str(id_token), ctx)

    salve.logger.info(
        '{0}: Generating Block From Identifier Token: {1}'.format(
            str(ctx), str(id_token))
        )

    # if the identifier is not in the map, raise an exception
    val = id_token.value.lower()
    try:
        return identifier_map[val](ctx)
    except KeyError:
        raise BlockException('Unknown block identifier ' + val, ctx)
