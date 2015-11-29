import abc
import os

import salve
from salve import with_metaclass
from salve.action.base import Action


class CopyAction(with_metaclass(abc.ABCMeta, Action)):
    """
    The base class for all CopyActions.

    A generic Copy takes a source and destination, and copies the
    source to the destination. The meanings of a Copy vary between
    files and directories, so this is an ABC.
    """
    verification_codes = (Action.verification_codes
                          .extend('UNWRITABLE_TARGET', 'UNREADABLE_SOURCE'))

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

    def canexec_non_ok_code(self, code):
        if code == self.verification_codes.UNWRITABLE_TARGET:
            salve.logger.warn(
                '{0}: {1}: Non-Writable target "{2}"'
                .format(self.file_context, self.prettyname, self.dst))
            return False
        elif code == self.verification_codes.UNREADABLE_SOURCE:
            salve.logger.warn(
                '{0}: {1}: Non-Readable source "{2}"'
                .format(self.file_context, self.prettyname, self.src))
            return False
        else:
            assert False

    def __str__(self):
        return ("{0}(src={1},dst={2},context={3!r})".format(
            self.prettyname, self.src, self.dst, self.file_context))
