#!/usr/bin/python

import abc
import os

from src.util.enum import Enum
from src.util.error import SALVEException
import src.util.locations as locations


class BlockException(SALVEException):
    """
    A SALVE exception specialized for blocks.
    """
    def __init__(self, msg, context):
        """
        BlockException constructor

        Args:
            @msg
            A string message that describes the error or exception.
            @context
            A SALVEContext that identifies the origin of this
            exception.
        """
        SALVEException.__init__(self, msg, context=context)


class Block(object):
    """
    A block is the basic unit of configuration.
    Typically, blocks describe files, SALVE manifests, patches, etc
    This is an ABC that defines the common characteristics of all
    blocks.
    """
    __metaclass__ = abc.ABCMeta

    # these are the valid types of block, and therefore the valid
    # block identifiers (case insensitive)
    types = Enum('FILE', 'MANIFEST', 'DIRECTORY')

    def __init__(self, ty, context):
        """
        Base Block constructor.

        Args:
            @ty
            An element of Block.types, the type of the block.

            @context
            The SALVEContext of this Block. Used to pass globals and
            state information to and from the block.
        """
        self.block_type = ty
        self.context = context
        # every block holds a hashmap of attribute names to values,
        # always initialized as empty
        self.attrs = {}
        # this is a set of attribute identifiers which always carry
        # a path as their value
        self.path_attrs = set()
        # this is a set of attribute identifiers which must be present
        # in order for the block to be valid
        self.min_attrs = set()

    def set(self, attribute_name, value):
        """
        Set an attribute of the block to have a specific value. Note
        that this is a destructive overwrite if the attribute had a
        previous value.

        Args:
            @attribute_name
            The attribute's identifier, typically converted to lower
            case.
            @value
            The value being assigned to the attribute. Typically a
            string.
        """
        self.attrs[attribute_name] = value

    def get(self, attribute_name):
        """
        Return the value of a given attribute of the block.

        Args:
            @attribute_name
            The attribute's identifier. Note that this is case
            sensitive.
        """
        return self.attrs[attribute_name]

    def has(self, attribute_name):
        """
        Checks if the block has a value associated with a given
        attribute. Returns the T/F value of that check.

        Args:
            @attribute_name
            The attribute's identifier. Note that this is case
            sensitive.
        """
        return attribute_name in self.attrs

    def ensure_has_attrs(self, *args):
        """
        Given a list of attributes, checks if the block has each of
        those attributes, and raises a BlockException on the first one
        that fails.

        Args:
            @args
            A variable argument list of attribute identifiers to be
            checked.
        """
        for attr in args:
            if not self.has(attr):
                raise self.mk_except('Block(ty=' + self.block_type + ') ' +
                                     'missing attr "' + attr + '"')

    def mk_except(self, msg):
        """
        Create a BlockException from the block. Used to easily pass the
        block's context to the exception, and to give any extra
        information that might be desirable for a specific block type.

        Args:
            @msg
            The string message that should be reported by the raised
            exception.
        """
        exc = BlockException(msg, self.context)
        return exc

    @abc.abstractmethod
    def to_action(self):
        """
        Converts the Block to an action. Does not modify the block
        itself. In this sense, all Blocks are factories.

        There is no meaningful implementation of this for an untyped
        block, so it is abstract.
        """
        return  # pragma: no cover

    def expand_file_paths(self, root_dir):
        """
        Expands all relative paths in a block's set of attribute values,
        given a directory to act as the prefix to all of the paths. The
        attributes are identified as paths based on the block type.

        Args:
            @root_dir
            The directory to be used as a prefix to all relative paths
            in the block.
        """
        # define a helper to expand attributes with the root_dir
        def expand_attr(attrname):
            val = self.get(attrname)
            if not locations.is_abs_or_var(val):
                self.set(attrname, os.path.join(root_dir, val))

        # find the minimal set of path attributes
        min_path_attrs = self.min_attrs.intersection(self.path_attrs)
        # ... and the non-minimal path attributes
        non_min_path_attrs = self.path_attrs.difference(min_path_attrs)

        # first ensure that the minimal attributes are in place
        self.ensure_has_attrs(*list(min_path_attrs))

        # and expand each one
        for attr in min_path_attrs:
            expand_attr(attr)

        # then ensure that any of the non-minimal ones that are present
        # are also expanded
        for attr in non_min_path_attrs:
            if self.has(attr):
                expand_attr(attr)
