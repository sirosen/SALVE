from salve import logger
from salve.action.create.base import CreateAction

from salve.context import ExecutionContext


class FileCreateAction(CreateAction):
    """
    An action to create a single file.
    """
    def __str__(self):
        return ("FileCreateAction(dst=" + self.dst +
                ",context=" + repr(self.file_context) + ")")

    def verify_can_exec(self, filesys):
        """
        Ensures that the target file exists and is writable, or that
        it does not exist and is in a writable directory.
        """
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        logstr = 'FileCreate: Checking target is writable, \"%s\"' % self.dst
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        if not filesys.writable_path_or_ancestor(self.dst):
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def execute(self, filesys):
        """
        FileCreateAction execution.

        Does a file creation if the file does not exist.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            logstr = ("FileCreate: Non-Writable target file \"%s\"" % self.dst)
            logger.warn('{0}: {1}'.format(self.file_context, logstr))
            return

        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        logstr = 'Performing File Creation of \"%s\"' % self.dst
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        # touch the file
        filesys.touch(self.dst)
