#!/usr/bin/python

# this is the block API, for designing and implementing block types

import abc

from salve.util import Enum, with_metaclass


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


class Block(with_metaclass(abc.ABCMeta)):
    """
    A block is the basic unit of configuration.
    Typically, blocks describe files, SALVE manifests, patches, etc
    This is an ABC that defines the common characteristics of all
    blocks. Furthermore, it defines the methods that must be implemented
    on a block by its author.
    """
    # these are the valid types of block, and therefore the valid
    # block identifiers (case insensitive)
    types = Enum('FILE', 'MANIFEST', 'DIRECTORY')

    @abc.abstractmethod
    def has(self, attribute_name):
        """
        Checks if the block has a value associated with a given
        attribute. Returns the T/F value of that check.

        Args:
            @attribute_name
            The attribute's identifier, converted to lower case.
        """
        return False  # pragma: no cover

    @abc.abstractmethod
    def set(self, attribute_name, value):
        """
        Set an attribute of the block to have a specific value. Note
        that this is a destructive overwrite if the attribute had a
        previous value.

        Args:
            @attribute_name
            The attribute's identifier, converted to lower case.
            @value
            The value being assigned to the attribute. Typically a
            string.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def get(self, attribute_name):
        """
        Return the value of a given attribute of the block.

        Args:
            @attribute_name
            The attribute's identifier, lower case.
        """
        return None  # pragma: no cover

    @abc.abstractmethod
    def compile(self):
        """
        Convert to a compiled block. Uses the existing has(), set(), and get()
        operations on the block, as well as leveraging the context if desired.
        No other operations may be relied on to exist.
        """
        return None  # pragma: no cover
