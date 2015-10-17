from salve import logger, paths
from salve.action.copy.base import CopyAction
from salve.filesys import access_codes
from salve.context import ExecutionContext


class DirCopyAction(CopyAction):
    """
    An action to copy a directory tree.
    """
    def __init__(self, src, dst, file_context):
        """
        DirCopyAction constructor.

        Args:
            @src
            Source path.
            @dst
            Destination path.
            @file_context
            The FileContext.
        """
        CopyAction.__init__(self, src, dst, file_context)

    def __str__(self):
        return ("DirCopyAction(src=" + str(self.src) + ",dst=" +
                str(self.dst) + ",context=" + repr(self.file_context) + ")")

    def verify_can_exec(self, filesys):
        """
        Check to ensure that execution can proceed without errors.
        Ensures that the the target directory is writable.
        """
        # transition to the action verification phase,
        # confirming execution will work
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        def readable_source():
            """
            Checks if the source is a readable and traversable directory. If
            not, then it will be impossible to view and copy its contents.
            """
            return filesys.access(self.src,
                                  access_codes.R_OK | access_codes.X_OK)

        def writable_target():
            """
            Checks if the target is in a writable directory.
            """
            return filesys.access(paths.dirname(self.dst),
                                  access_codes.W_OK)

        logstr = ('DirCopy: Checking source is readable + traversable, ' +
                  '{0}'.format(self.dst))
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        if not readable_source():
            return self.verification_codes.UNREADABLE_SOURCE

        logger.info(
            ('{0}: DirCopy: Checking target is writeable, \"{1}\"').format(
                self.file_context, self.dst)
            )

        if not writable_target():
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def execute(self, filesys):
        """
        Copy a directory tree from one location to another.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.UNREADABLE_SOURCE:
            logstr = "DirCopy: Non-Readable source directory \"%s\"" % self.src
            logger.warn('{0}: {1}'.format(self.file_context, logstr))
            return

        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            logstr = "DirCopy: Non-Writable target directory \"%s\"" % self.dst
            logger.warn('{0}: {1}'.format(self.file_context, logstr))
            return

        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        logstr = ('Performing Directory Copy \"%s\" -> \"%s\"' %
                  (self.src, self.dst))
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        filesys.copy(self.src, self.dst)
