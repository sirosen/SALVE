import abc

from salve import logger, ugo, with_metaclass
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

    def verify_can_exec(self, filesys):
        # transition to the action verification phase,
        # confirming execution will work
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        logger.info('Chown: Checking target exists, \"%s\"' %
                    self.target)

        if not filesys.exists(self.target):
            return self.verification_codes.NONEXISTENT_TARGET

        logger.info('Chown: Checking if execution can be skipped, ' +
                    '\"%s\"' % self.target)

        # if the chown would do nothing, give skip exec
        if ugo.name_to_uid(self.user) == filesys.stat(self.target).st_uid and \
           ugo.name_to_gid(self.group) == filesys.stat(self.target).st_gid:
            return self.verification_codes.SKIP_EXEC

        logger.info('Chown: Checking user is root')

        if not ugo.is_root():
            return self.verification_codes.NOT_ROOT

        return self.verification_codes.OK
