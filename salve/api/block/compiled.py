#!/usr/bin/python

import abc

from salve import with_metaclass


class CompiledBlock(with_metaclass(abc.ABCMeta)):
    """
    To define a block, you need to write a block definition in the block-def
    DSL, and you need to write a definition for the compiled block. The block
    will be produced by parsing a manifest, but the compiled block defines what
    actions are taken by means of that block.
    """
    @abc.abstractmethod
    def verify_can_exec(self):
        """
        Verifies that the compiled block can be executed.

        This attempts to verify that there are no actions specified by the
        block that will fail during execution.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def execute(self):
        """
        Executes the compiled block.

        This is the only essential characteristic of a compiled block: that
        it can be executed to produce some effect.
        """
        pass  # pragma: no cover
