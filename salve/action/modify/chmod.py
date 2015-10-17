import abc

from salve import logger, ugo, with_metaclass
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

    def verify_can_exec(self, filesys):
        # transition to the action verification phase,
        # confirming execution will work
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        logger.info('Chmod: Checking target exists, \"%s\"' %
                    self.target)

        # a nonexistent file or dir can never be chmoded
        if not filesys.exists(self.target):
            return self.verification_codes.NONEXISTENT_TARGET

        logger.info('Chmod: Checking if user is root')

        # as root, you can always perform a chmod on existing files
        if ugo.is_root():
            return self.verification_codes.OK

        logger.info('Chmod: Checking if user is owner of target, ' +
                    '\"%s\"' % self.target)

        # now the file is known to exist and the user is not root
        if not ugo.is_owner(self.target):
            return self.verification_codes.UNOWNED_TARGET

        return self.verification_codes.OK
