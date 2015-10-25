from salve import logger
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
        return ("FileChmodAction(target=" + str(self.target) +
                ",mode=" + '{0:o}'.format(self.mode) +
                ",context=" + repr(self.file_context) + ")")

    def execute(self, filesys):
        """
        FileChmodAction execution.

        Change the umask of a single file.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.NONEXISTENT_TARGET:
            logstr = "FileChmod: Non-Existent target file \"%s\"" % self.target
            logger.warn(logstr)
            return
        if vcode == self.verification_codes.UNOWNED_TARGET:
            logstr = "FileChmod: Unowned target file \"%s\"" % self.target
            logger.warn(logstr)
            return

        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        logger.info('Performing FileChmod of \"%s\" to %s' %
                    (self.target, '{0:o}'.format(self.mode)))

        filesys.chmod(self.target, self.mode)
