import salve
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

        salve.logger.info(
            '{0}: FileCopy: Checking destination is writable, "{1}"'
            .format(self.file_context, self.dst))

        if not filesys.writable_path_or_ancestor(self.dst):
            return self.verification_codes.UNWRITABLE_TARGET

        salve.logger.info('{0}: FileCopy: Checking if source is link, "{1}"'
                          .format(self.file_context, self.src))

        if filesys.lookup_type(self.src) is filesys.element_types.LINK:
            return self.verification_codes.OK

        salve.logger.info('{0}: FileCopy: Checking source is readable, "{1}"'
                          .format(self.file_context, self.src))

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
            salve.logger.warn('{0}: FileCopy: Non-Writable target file "{1}"'
                              .format(self.file_context, self.dst))
            return

        if vcode == self.verification_codes.UNREADABLE_SOURCE:
            salve.logger.warn('{0}: FileCopy: Non-Readable source file "{1}"'
                              .format(self.file_context, self.src))
            return

        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('{0}: Performing File Copy "{1}" -> "{2}"'
                          .format(self.file_context, self.src, self.dst))

        filesys.copy(self.src, self.dst)
