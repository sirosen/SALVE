from nose.tools import istest

from tests.util import ensure_except
from salve.parser import Token
from salve.exceptions import BlockException

from salve.block import identifier, FileBlock, ManifestBlock, DirBlock

from tests.unit.block import dummy_file_context, ScratchWithExecCtx


def _mk_id_token(name):
    return Token(name, Token.types.IDENTIFIER, dummy_file_context)


def _block_from_name(name):
    return identifier.block_from_identifier(_mk_id_token(name))


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
    def valid_file_id(self):
        """
        Unit: Block Identifier File Identifier To Block
        Checks that an identifier 'file' creates a file block.
        """
        assert isinstance(_block_from_name('file'), FileBlock)

    @istest
    def valid_manifest_id(self):
        """
        Unit: Block Identifier Manifest Identifier To Block
        Checks that an identifier 'manifest' creates a manifest block.
        """
        assert isinstance(_block_from_name('manifest'), ManifestBlock)

    @istest
    def valid_directory_id(self):
        """
        Unit: Block Identifier Directory Identifier To Block
        Checks that an identifier 'directory' creates a directory block.
        """
        assert isinstance(_block_from_name('directory'), DirBlock)
