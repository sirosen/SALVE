import abc

from salve import Enum, with_metaclass


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
    def __contains__(self, attribute_name):
        """
        Checks if the block has a value associated with a given
        attribute. Returns the T/F value of that check.

        Args:
            @attribute_name
            The attribute's identifier, converted to lower case.
        """
        return False  # pragma: no cover

    @abc.abstractmethod
    def __setitem__(self, attribute_name, value):
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
    def __getitem__(self, attribute_name):
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
