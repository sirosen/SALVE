import abc
import os

from salve import with_metaclass
from salve.action.base import Action


class CopyAction(with_metaclass(abc.ABCMeta, Action)):
    """
    The base class for all CopyActions.

    A generic Copy takes a source and destination, and copies the
    source to the destination. The meanings of a Copy vary between
    files and directories, so this is an ABC.
    """
    verification_codes = \
        Action.verification_codes.extend('UNWRITABLE_TARGET',
                                         'UNREADABLE_SOURCE')

    def __init__(self, src, dst, file_context):
        """
        CopyAction constructor.

        Args:
            @src
            The source path (file being copied).
            @dst
            The destination path (being copied to).
            @file_context
            The FileContext.
        """
        Action.__init__(self, file_context)
        self.src = os.path.normpath(src)
        self.dst = os.path.normpath(dst)

    def __str__(self):
        return ("{0}(src={1},dst={2},context={3})"
                .format(self.__class__.__name__, self.src, self.dst,
                        repr(self.file_context)))
