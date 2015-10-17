from salve import logger, paths
from salve.action.create.base import CreateAction

from salve.filesys import access_codes
from salve.context import ExecutionContext


class FileCreateAction(CreateAction):
    """
    An action to create a single file.
    """
    def __init__(self, dst, file_context):
        """
        FileCreateAction constructor.

        Args:
            @dst
            Destination path.
            @file_context
            The FileContext.
        """
        CreateAction.__init__(self, file_context)
        self.dst = dst

    def __str__(self):
        return ("FileCreateAction(dst=" + self.dst +
                ",context=" + repr(self.file_context) + ")")

    def verify_can_exec(self, filesys):
        """
        Ensures that the target file exists and is writable, or that
        it does not exist and is in a writable directory.
        """
        # transition to the action verification phase,
        # confirming execution will work
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        def writable_target():
            """
            Checks if the target is in a writable directory.
            """
            if filesys.access(self.dst, access_codes.W_OK):
                return True
            if filesys.access(self.dst, access_codes.F_OK):
                return False
            # file is now known not to exist
            assert not filesys.exists(self.dst)

            parent = paths.dirname(self.dst)
            if filesys.access(parent, access_codes.W_OK):
                return True

            # the file is doesn't exist and the containing dir is
            # not writable or doesn't exist
            return False

        logstr = 'FileCreate: Checking target is writable, \"%s\"' % self.dst
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        if not writable_target():
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

        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        logstr = 'Performing File Creation of \"%s\"' % self.dst
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        # touch the file
        filesys.touch(self.dst)
