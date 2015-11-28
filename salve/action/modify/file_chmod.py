import salve
from salve.action.modify.chmod import ChmodAction
from salve.context import ExecutionContext


class FileChmodAction(ChmodAction):
    """
    A ChmodAction applied to a single file.
    """
    def __init__(self, target, mode, file_context):
        """
        FileChmodAction constructor.

        Args:
            @target
            Path to the file to chmod.
            @mode
            The new umask of @target.
            @file_context
            The FileContext.
        """
        ChmodAction.__init__(self, target, mode, file_context)

    def __str__(self):
        return '{0}(target={1},mode={2:o},context={3!r})'.format(
            self.prettyname, self.target, self.mode, self.file_context)

    def execute(self, filesys):
        """
        FileChmodAction execution.

        Change the umask of a single file.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.NONEXISTENT_TARGET:
            salve.logger.warn('FileChmod: Non-Existent target file "{0}"'
                              .format(self.target))
            return
        if vcode == self.verification_codes.UNOWNED_TARGET:
            salve.logger.warn('FileChmod: Unowned target file "{0}"'
                              .format(self.target))
            return

        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing FileChmod of "{0}" to {1:o}'
                          .format(self.target, self.mode))

        filesys.chmod(self.target, self.mode)
