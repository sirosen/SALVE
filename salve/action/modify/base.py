import abc
from salve import with_metaclass
from salve.action.base import Action


class ModifyAction(with_metaclass(abc.ABCMeta, Action)):
    """
    The base class for all Actions that modify existing files and
    directories.
    """
    verification_codes = \
        Action.verification_codes.extend('NONEXISTENT_TARGET')

    def __init__(self, target, file_context):
        """
        ModifyAction constructor.

        Args:
            @target
            The path to the file or dir to modify.
            @file_context
            The SALVEContext.
        """
        Action.__init__(self, file_context)
        self.target = target
