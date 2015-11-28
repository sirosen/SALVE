import abc

from salve import with_metaclass
from salve.action.base import Action


class CreateAction(with_metaclass(abc.ABCMeta, Action)):
    """
    The base class for all CreateActions.

    Extends verification codes to include UNWRITABLE_TARGET as an error
    condition.
    """
    verification_codes = \
        Action.verification_codes.extend('UNWRITABLE_TARGET')

    def __init__(self, dst, file_context):
        """
        CreateAction initializer

        Args:
            @dst
            Destination path.
            @file_context
            The FileContext.
        """
        Action.__init__(self, file_context)
        self.dst = dst

    def __str__(self):
        return '{0}(dst={1},context={2!r})'.format(
            self.prettyname, self.dst, self.file_context)
