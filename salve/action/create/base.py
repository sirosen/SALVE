import abc

import salve
from salve import with_metaclass
from salve.context import ExecutionContext
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

    def get_verification_code(self, filesys):
        """
        Checks if the target already exists, or if its parent is writable.
        """
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        salve.logger.debug(
            '{0}: {1}: Checking target is writable, "{2}"'
            .format(self.file_context, self.prettyname, self.dst))

        if not filesys.writable_path_or_ancestor(self.dst):
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def canexec_non_ok_code(self, code):
        if code is self.verification_codes.UNWRITABLE_TARGET:
            salve.logger.warn(
                '{0}: {1}: Non-Writable target "{2}"'
                .format(self.file_context, self.prettyname, self.dst))
            return False

    def __str__(self):
        return '{0}(dst={1},context={2!r})'.format(
            self.prettyname, self.dst, self.file_context)
