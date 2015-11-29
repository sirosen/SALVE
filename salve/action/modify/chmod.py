import abc

import salve
from salve import ugo, with_metaclass
from salve.action.modify.base import ModifyAction
from salve.context import ExecutionContext


class ChmodAction(with_metaclass(abc.ABCMeta, ModifyAction)):
    """
    The base class for ChmodActions.
    Is an ABC.
    """
    verification_codes = \
        ModifyAction.verification_codes.extend('UNOWNED_TARGET')

    def __init__(self, target, mode, file_context):
        """
        ChmodAction constructor.

        Args:
            @target
            Path to the dir or file to modify.
            @mode
            The new umask of @target.
            @file_context
            The FileContext.
        """
        ModifyAction.__init__(self, target, file_context)
        self.mode = int(mode, 8)

    def canexec_non_ok_code(self, code):
        if code is self.verification_codes.NONEXISTENT_TARGET:
            salve.logger.warn('{0}: Non-Existent target "{1}"'
                              .format(self.prettyname, self.target))
            return False
        elif code is self.verification_codes.UNOWNED_TARGET:
            salve.logger.warn('{0}: Unowned target "{1}"'
                              .format(self.prettyname, self.target))
            return False

    def get_verification_code(self, filesys):
        # transition to the action verification phase,
        # confirming execution will work
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        salve.logger.debug('{0}: Checking target exists, "{1}"'
                           .format(self.prettyname, self.target))

        # a nonexistent file or dir can never be chmoded
        if not filesys.exists(self.target):
            return self.verification_codes.NONEXISTENT_TARGET

        salve.logger.debug('{0}: Checking if user is root'
                           .format(self.prettyname))

        # as root, you can always perform a chmod on existing files/dirs
        if ugo.is_root():
            return self.verification_codes.OK

        salve.logger.debug('{0}: Checking if user is owner of target, "{1}"'
                           .format(self.prettyname, self.target))

        # now the file is known to exist and the user is not root
        if not ugo.is_owner(self.target):
            return self.verification_codes.UNOWNED_TARGET

        return self.verification_codes.OK
