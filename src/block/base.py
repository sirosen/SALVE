#!/usr/bin/python

import abc

from src.util.enum import Enum
from src.util.error import SALVEException

class BlockException(SALVEException):
    """
    A SALVE exception specialized for blocks.
    """
    def __init__(self,msg,context):
        """
        BlockException constructor

        Args:
            @msg
            A string message that describes the error or exception.
            @context
            A StreamContext that identifies the origin of this
            exception.
        """
        SALVEException.__init__(self,msg,context)

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
    types = Enum('FILE','MANIFEST','DIRECTORY')

    def __init__(self,ty,context=None):
        """
        Base Block constructor.

        Args:
            @ty
            An element of Block.types, the type of the block.

        KWargs:
            @context
            The StreamContext from which this block originates.
            Specifies the filename and line number of the stream at
            which this block's identifier can be found, in order to tie
            error messages to a specific block declaration.
            Defaults to None for cases where the block is synthesized
            by unusual means (for example, the root manifest block).
        """
        self.block_type = ty
        self.context = context
        # every block holds a hashmap of attribute names to values,
        # always initialized as empty
        self.attrs = {}

    def set(self,attribute_name,value):
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

    def get(self,attribute_name):
        """
        Return the value of a given attribute of the block.

        Args:
            @attribute_name
            The attribute's identifier. Note that this is case
            sensitive.
        """
        return self.attrs[attribute_name]

    def has(self,attribute_name):
        """
        Checks if the block has a value associated with a given
        attribute. Returns the T/F value of that check.

        Args:
            @attribute_name
            The attribute's identifier. Note that this is case
            sensitive.
        """
        return attribute_name in self.attrs

    def ensure_has_attrs(self,*args):
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
                raise self.mk_except('Block(ty='+self.block_type+') '+\
                                          'missing attr "'+attr+'"')

    def mk_except(self,msg):
        """
        Create a BlockException from the block. Used to easily pass the
        block's context to the exception.

        Args:
            @msg
            The string message that should be reported by the raised
            exception.
        """
        exc = BlockException(msg,self.context)
        return exc

    @abc.abstractmethod
    def to_action(self):
        """
        Converts the Block to an action. Does not modify the block
        itself. In this sense, all Blocks are factories.

        There is no meaningful implementation of this for an untyped
        block, so it is abstract.
        """
        return #pragma: no cover

    @abc.abstractmethod
    def expand_file_paths(self, root_dir):
        """
        Expands all relative paths in a block's set of attribute values,
        given a directory to act as the prefix to all of the paths. The
        attributes are identified as paths based on the block type.

        There is no meaningful implementation of this for an untyped
        block, so it is abstract.
        """
        return #pragma: no cover
