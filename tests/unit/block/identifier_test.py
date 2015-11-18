from nose.tools import istest

from tests.framework import ensure_except
from salve.parser import Token
from salve.exceptions import BlockException

from salve.block import identifier, FileBlock, ManifestBlock, DirBlock

from tests.unit.block import dummy_file_context, ScratchWithExecCtx


def _block_from_name(name):
    return identifier.block_from_identifier(
        Token(name, Token.types.IDENTIFIER, dummy_file_context))


class TestWithLoggerPatch(ScratchWithExecCtx):
    @istest
    def invalid_block_id1(self):
        """
        Unit: Block Identifier Invalid Identifier Fails (1)
        Checks that an invalid block identifier fails, even when it is of
        type IDENTIFIER.
        """
        ensure_except(BlockException, _block_from_name, 'invalid_block_id')

    @istest
    def invalid_block_id2(self):
        """
        Unit: Block Identifier Invalid Identifier Fails (2)
        Checks that an invalid block identifier with a non-IDENTIFIER type
        fails block creation.
        """
        bad_id = Token('invalid_block_id', Token.types.TEMPLATE,
                       dummy_file_context)
        ensure_except(BlockException, identifier.block_from_identifier, bad_id)

    @istest
    def valid_block_id_test_generator(self):
        params = [
            ('file', FileBlock, 'File'),
            ('manifest', ManifestBlock, 'Manifest'),
            ('directory', DirBlock, 'Directory'),
        ]
        for (tok, klass, name) in params:
            def check():
                assert isinstance(_block_from_name(tok), klass)
            check.description = (
                'Unit: {0} Identifier File Identifier To Block'
                .format(name))

            yield check
