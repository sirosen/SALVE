import mock
from nose.tools import istest
from tests.util import ensure_except, full_path

from salve import paths
from salve.context import ExecutionContext
from salve.exceptions import BlockException

from salve.block import ManifestBlock, FileBlock

from tests.unit.block import dummy_file_context, dummy_conf, ScratchWithExecCtx
from .helpers import check_list_act


def _man_block_and_containing_dir(name):
    return (ManifestBlock(dummy_file_context, source=full_path(name)),
            paths.containing_dir(full_path(name)))


class TestWithScratchdir(ScratchWithExecCtx):
    def setUp(self):
        ScratchWithExecCtx.setUp(self)
        ExecutionContext()['config'] = dummy_conf

    @istest
    def sourceless_manifest_compile_error(self):
        """
        Unit: Manifest Compilation Fails Without Action
        Verifies that a Manifest block raises a BlockException when
        compiled if the action attribute is unspecified.
        """
        b = ManifestBlock(dummy_file_context)
        ensure_except(BlockException, b.compile)

    @istest
    def sourceless_manifest_expand_error(self):
        """
        Unit: Manifest Block Path Expand Fails Without Source
        Verifies that a Manifest block raises a BlockException when paths
        are expanded if the source attribute is unspecified.
        """
        b = ManifestBlock(dummy_file_context)
        ensure_except(BlockException, b.expand_blocks, '/', False)

    @istest
    def empty_manifest_expand(self):
        """
        Unit: Manifest Block SubBlock Expand Empty List
        Verifies that a Manifest block with no sub-blocks expands without
        errors.
        """
        b, d = _man_block_and_containing_dir('empty.manifest')
        b.expand_blocks('/', False)
        assert len(b.sub_blocks) == 0

    @istest
    def recursive_manifest_error(self):
        """
        Unit: Manifest Block Self-Inclusion Error
        Verifies that a Manifest block which includes itself raises a
        BlockException when expanded.
        """
        b, d = _man_block_and_containing_dir('self_include.manifest')
        ensure_except(BlockException, b.expand_blocks, d, False)

    @istest
    def sub_block_expand(self):
        """
        Unit: Manifest Block SubBlock Expand
        Verifies that Manifest block expansion works normally.
        """
        b, d = _man_block_and_containing_dir('empty_and_file.manifest')
        b.expand_blocks(d, False)
        assert len(b.sub_blocks) == 2
        mblock = b.sub_blocks[0]
        fblock = b.sub_blocks[1]
        assert isinstance(mblock, ManifestBlock)
        assert isinstance(fblock, FileBlock)
        assert mblock['source'] == full_path('empty.manifest')
        assert fblock['source'] == full_path('empty.manifest')
        assert fblock['target'] == paths.pjoin(d, 'a/b/c')

    @istest
    @mock.patch('os.path.exists', lambda f: True)
    @mock.patch('os.access', lambda f, p: True)
    def sub_block_compile(self):
        """
        Unit: Manifest Block SubBlock Compile
        Verifies that Manifest block expansion followed by action
        conversion works normally.
        """
        b, d = _man_block_and_containing_dir('empty_and_file.manifest')
        b.expand_blocks(d, False)

        act = b.compile()

        check_list_act(act, 2)
        check_list_act(act.actions[0], 0)
        check_list_act(act.actions[1], 4)
