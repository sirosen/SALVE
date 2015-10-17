from salve import logger, paths
from salve.action.copy.base import CopyAction
from salve.filesys import access_codes
from salve.context import ExecutionContext


class FileCopyAction(CopyAction):
    """
    An action to copy a single file.
    """
    def __init__(self, src, dst, file_context):
        """
        FileCopyAction constructor.

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
        """
        Stringification into type, source, dst, and context.
        """
        return ("FileCopyAction(src=" + str(self.src) + ",dst=" +
                str(self.dst) + ",context=" + repr(self.file_context) + ")")

    def verify_can_exec(self, filesys):
        """
        Check to ensure that execution can proceed without errors.
        Ensures that the source file exists and is readable, and that
        the target file can be created or is writable.
        """
        # transition to the action verification phase,
        # confirming execution will work
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        def writable_target():
            """
            Checks if the target file is writable.
            """
            if filesys.access(self.dst, access_codes.W_OK):
                return True
            if filesys.access(self.dst, access_codes.F_OK):
                return False

            # at this point, the file is known not to exist
            # now check properties of the containing dir
            containing_dir = paths.dirname(self.dst)
            if filesys.access(containing_dir, access_codes.W_OK):
                return True

            # if the file doesn't exist, and the dir containing it
            # isn't writable, then the file can't be written
            return False

        def readable_source():
            """
            Checks if the source is a readable file.
            """
            return filesys.access(self.src, access_codes.R_OK)

        def source_islink():
            """
            Checks if the source is a symlink (copied by value, not
            dereferenced)
            """
            return filesys.lookup_type(self.src) is filesys.element_types.LINK

        logstr = 'FileCopy: Checking destination is writable, \"%s\"' % \
            self.dst
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        if not writable_target():
            return self.verification_codes.UNWRITABLE_TARGET

        logstr = 'FileCopy: Checking if source is link, "%s"' % self.src
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        if source_islink():
            return self.verification_codes.OK

        logstr = 'FileCopy: Checking source is readable, \"%s\"' % self.src
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        if not readable_source():
            return self.verification_codes.UNREADABLE_SOURCE

        return self.verification_codes.OK

    def execute(self, filesys):
        """
        FileCopyAction execution.

        Does a file copy or symlink creation, depending on the type
        of the source file.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            logstr = "FileCopy: Non-Writable target file \"%s\"" % self.dst
            logger.warn('{0}: {1}'.format(self.file_context, logstr))
            return

        if vcode == self.verification_codes.UNREADABLE_SOURCE:
            logstr = "FileCopy: Non-Readable source file \"%s\"" % self.src
            logger.warn('{0}: {1}'.format(self.file_context, logstr))
            return

        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        logstr = 'Performing File Copy \"%s\" -> \"%s\"' % (self.src, self.dst)
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        filesys.copy(self.src, self.dst)
