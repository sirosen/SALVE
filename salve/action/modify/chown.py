import abc

import salve
from salve import ugo, with_metaclass
from salve.action.modify.base import ModifyAction
from salve.context import ExecutionContext


class ChownAction(with_metaclass(abc.ABCMeta, ModifyAction)):
    """
    The base class for ChownActions.
    Is an ABC.
    """
    verification_codes = \
        ModifyAction.verification_codes.extend('NOT_ROOT',
                                               'SKIP_EXEC')

    def __init__(self, target, user, group, file_context):
        """
        ChownAction constructor.

        Args:
            @target
            Path to the dir or file to modify.
            @user
            The new user of @target.
            @group
            The new group of @target.
            @file_context
            The FileContext.
        """
        ModifyAction.__init__(self, target, file_context)
        self.user = user
        self.group = group

    def canexec_non_ok_code(self, code):
        if code is self.verification_codes.NONEXISTENT_TARGET:
            salve.logger.warn('{0}: Non-Existent target "{1}"'
                              .format(self.prettyname, self.target))
            return False
        elif code == self.verification_codes.NOT_ROOT:
            salve.logger.warn("{0}: Cannot Chown as Non-Root User"
                              .format(self.prettyname))
            return False
        # if verification says that we skip without performing any action
        # then there should be no warning message
        elif code == self.verification_codes.SKIP_EXEC:
            return False

    def get_verification_code(self, filesys):
        # transition to the action verification phase,
        # confirming execution will work
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        salve.logger.debug('{0}: Checking target exists, "{1}"'
                           .format(self.prettyname, self.target))

        if not filesys.exists(self.target):
            return self.verification_codes.NONEXISTENT_TARGET

        salve.logger.debug('{0}: Checking if execution can be skipped, "{1}"'
                           .format(self.prettyname, self.target))

        # if the chown would do nothing, give skip exec
        if ugo.name_to_uid(self.user) == filesys.stat(self.target).st_uid and \
           ugo.name_to_gid(self.group) == filesys.stat(self.target).st_gid:
            return self.verification_codes.SKIP_EXEC

        salve.logger.info('{0}: Checking user is root'.format(self.prettyname))

        if not ugo.is_root():
            return self.verification_codes.NOT_ROOT

        return self.verification_codes.OK
