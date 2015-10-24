from salve import logger
from salve.action.copy.base import CopyAction
from salve.filesys import access_codes
from salve.context import ExecutionContext


class FileCopyAction(CopyAction):
    def verify_can_exec(self, filesys):
        """
        Check to ensure that execution can proceed without errors.
        Ensures that the source file exists and is readable, and that
        the target file can be created or is writable.
        """
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        logstr = 'FileCopy: Checking destination is writable, \"%s\"' % \
            self.dst
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        if not filesys.writable_path_or_ancestor(self.dst):
            return self.verification_codes.UNWRITABLE_TARGET

        logstr = 'FileCopy: Checking if source is link, "%s"' % self.src
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        if filesys.lookup_type(self.src) is filesys.element_types.LINK:
            return self.verification_codes.OK

        logstr = 'FileCopy: Checking source is readable, \"%s\"' % self.src
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        if not filesys.access(self.src, access_codes.R_OK):
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

        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        logstr = 'Performing File Copy \"%s\" -> \"%s\"' % (self.src, self.dst)
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        filesys.copy(self.src, self.dst)
