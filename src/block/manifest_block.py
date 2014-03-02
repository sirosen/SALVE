#!/usr/bin/python

import os

import src.execute.action as action

from src.util.context import ExecutionContext
from src.block.base import Block

class ManifestBlock(Block):
    """
    A manifest block describes another manifest to be expanded and
    executed. It may also specify properties of that manifest's
    execution. For example, if a manifest's blocks can be executed
    in parallel, or if its execution is conditional on a file existing.
    """
    def __init__(self,context,source=None):
        """
        Manifest Block constructor.

        Args:
            @context
            The SALVEContext for this block.

        KWArgs:
            @source
            The file from which this block is constructed.
        """
        # transition to the parsing/block expansion phase, converting
        # files into blocks
        context.transition(ExecutionContext.phases.PARSING)
        Block.__init__(self,Block.types.MANIFEST,context)
        self.sub_blocks = None
        if source:
            self.set('source',source)
        self.path_attrs.add('source')
        self.min_attrs.add('source')

    def expand_blocks(self,root_dir,config,ancestors=None):
        """
        Expands a manifest block by reading its source, parsing it into
        blocks, and assigning those to be the sub_blocks of the manifest
        block, forming a block tree. This is, in a certain sense, part
        of the parser.

        Args:
            @config is used to fill in any variable values in the
            blocks' template string attributes.
            @root_dir is the root of all relative paths in the manifest
            and its descendants. Typically, this is left unset and
            defaults to the SALVE_ROOT.

        KWArgs:
            @ancestors is the set of containing manifests. It is passed
            through invocations in order to ensure that there are no
            manifest loops.
        """
        # This import must take place inside of the function because
        # there is a circular dependency between ManifestBlocks and the
        # parser
        import src.reader.parse as parse
        # ensure that this block has config applied and paths expanded
        # this guarantees that 'source' is accurate
        config.apply_to_block(self)
        self.expand_file_paths(root_dir)
        self.ensure_has_attrs('source')
        filename = self.get('source')

        # We don't default ancestors=set() because that is only
        # evaluated once, which would cause strange problems with
        # multiple independent invocations of expand_blocks
        if not ancestors: ancestors = set()
        if filename in ancestors:
            raise self.mk_except('Manifest ' + filename +\
                                      ' includes itself')
        ancestors.add(filename)

        # parse the manifest source
        with open(filename) as man:
            self.sub_blocks = parse.parse_stream(self.context,man)
        for b in self.sub_blocks:
            # recursively apply to manifest blocks
            if isinstance(b,ManifestBlock):
                b.expand_blocks(root_dir,
                                config,
                                ancestors=ancestors)
            # expand any relative paths and substitute for any vars
            # must be in order so that a variable which expands to a
            # relative path works correctly
            else:
                config.apply_to_block(b)
                b.expand_file_paths(root_dir)

    def to_action(self):
        """
        Uses the ManifestBlock to produce an action.
        The action will always be an actionlist of the expansion of
        the manifest block's sub-blocks.
        """
        # transition to the action conversion phase, converting
        # blocks into actions
        self.context.transition(ExecutionContext.phases.ACTION_CONVERSION)
        if self.sub_blocks is None:
            raise self.mk_except('Attempted to convert unexpanded '+\
                                 'manifest to action.')

        act = action.ActionList([],self.context)
        for b in self.sub_blocks:
            subact = b.to_action()
            if subact is not None:
                act.append(subact)

        return act
