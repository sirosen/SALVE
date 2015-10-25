import abc

from salve.action.modify.base import ModifyAction

from salve import with_metaclass


class DirModifyAction(with_metaclass(abc.ABCMeta, ModifyAction)):
    """
    The base class for Modify Actions on directories.
    Primarily used to carry information about the recursivity of the
    modification.
    Is an ABC.
    """
    def __init__(self, target, recursive, file_context):
        """
        DirModifyAction constructor.

        Args:
            @target
            Path to the dir to modify.
            @recursive
            If true, apply the modification to any contained files and
            dirs.
            @file_context
            The FileContext.
        """
        ModifyAction.__init__(self, target, file_context)
        self.recursive = recursive
