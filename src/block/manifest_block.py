#!/usr/bin/python

import os

import src.execute.action as action
import src.util.locations as locations
import src.reader.parse as parse

from src.block.base_block import Block, BlockException

class ManifestBlock(Block):
    """
    A manifest block describes another manifest to be expanded and
    executed. It may also specify properties of that manifest's
    execution. For example, if a manifest's blocks can be executed
    in parallel, or if its execution is conditional on a file existing.
    """
    def __init__(self,source=None):
        Block.__init__(self,Block.types.MANIFEST)
        self.sub_blocks = None
        if source: self.set('source',source)

    def expand_blocks(self,config,recursive=True,ancestors=None,root_dir=None):
        """
        Expands a manifest block by reading its source, parsing it into
        blocks, and assigning those to be the sub_blocks of the manifest
        block, forming a block tree. This is, in a certain sense, part
        of the parser.
        The @config is used to fill in any variable values in the
        blocks' template string attributes.
        When @recursive=False, this does not recurse, but in the general
        case, @recursive=True. This means that any manifest blocks in
        the sub_blocks are expanded as well.
        @ancestors is the set of containing manifests. It is passed
        through invocations in order to ensure that there are no
        manifest loops.
        @root_dir is the root of all relative paths in the manifest and
        its descendants. Typically, this is left unset and defaults to
        the SALVE_ROOT.
        """
        self.ensure_has_attrs('source')
        filename = self.get('source')

        # We don't default ancestors=set() because that is only
        # evaluated once, which would cause strange problems with
        # multiple independent invocations of expand_blocks
        if not ancestors: ancestors = set()
        if filename in ancestors:
            raise BlockException('Manifest ' + filename +\
                                 ' includes itself')
        ancestors.add(filename)

        # parse the manifest source
        with open(filename) as man:
            self.sub_blocks = parse.parse_stream(man)
        for b in self.sub_blocks:
            # expand any relative paths and substitute for any vars
            b.expand_file_paths(root_dir=root_dir)
            config.apply_to_block(b)
            # if set, recursively apply to manifest blocks
            if recursive and isinstance(b,ManifestBlock):
                b.expand_blocks(config,
                                ancestors=ancestors,
                                root_dir=root_dir)

    def expand_file_paths(self,root_dir=None):
        """
        Expand relative paths in source and target to be absolute paths
        beginning with the SALVE_ROOT.
        """
        self.ensure_has_attrs('source')

        if not locations.is_abs_or_var(self.get('source')):
            if not root_dir: root_dir = locations.get_salve_root()
            self.set('source',os.path.join(root_dir,
                                           self.get('source')))

    def to_action(self):
        if self.sub_blocks is None:
            raise BlockException('Attempted to convert unexpanded '+\
                                 'manifest to action.')
        return action.ActionList([b.to_action()
                                  for b in self.sub_blocks])
