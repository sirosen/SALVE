import salve
from salve import ugo
from salve.action.modify.chown import ChownAction
from salve.context import ExecutionContext


class FileChownAction(ChownAction):
    """
    A ChownAction applied to a single file.
    """
    def __init__(self, target, user, group, file_context):
        """
        FileChownAction constructor.

        Args:
            @target
            Path to the file to chown.
            @user
            The new user of @target.
            @group
            The new group of @target.
            @file_context
            The FileContext.
        """
        ChownAction.__init__(self, target, user, group, file_context)

    def __str__(self):
        return ("FileChownAction(target=" + str(self.target) +
                ",user=" + str(self.user) + ",group=" + str(self.group) +
                ",context=" + repr(self.file_context) + ")")

    def execute(self, filesys):
        """
        FileChownAction execution.

        Change the owner and group of a single file.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.NONEXISTENT_TARGET:
            salve.logger.warn('FileChown: Non-Existent target file "{0}"'
                              .format(self.target))
            return
        if vcode == self.verification_codes.NOT_ROOT:
            salve.logger.warn("FileChown: Cannot Chown as Non-Root User")
            return
        # if verification says that we skip without performing any action
        # then there should be no warning message
        if vcode == self.verification_codes.SKIP_EXEC:
            return

        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing FileChown of "{0}" to {1}:{2}'
                          .format(self.target, self.user, self.group))

        # chown without following symlinks
        filesys.chown(self.target, ugo.name_to_uid(self.user),
                      ugo.name_to_gid(self.group))
