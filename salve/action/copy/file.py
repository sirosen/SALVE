import salve
from salve.action.copy.base import CopyAction
from salve.filesys import access_codes
from salve.context import ExecutionContext


class FileCopyAction(CopyAction):
    def get_verification_code(self, filesys):
        """
        Ensures that the source file exists and is readable, and that
        the target file can be created or is writable.
        """
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        salve.logger.debug(
            '{0}: {1}: Checking destination is writable, "{2}"'
            .format(self.file_context, self.prettyname, self.dst))

        if not filesys.writable_path_or_ancestor(self.dst):
            return self.verification_codes.UNWRITABLE_TARGET

        salve.logger.debug(
            '{0}: {1}: Checking if source is link, "{2}"'
            .format(self.file_context, self.prettyname, self.src))

        if filesys.lookup_type(self.src) is filesys.element_types.LINK:
            return self.verification_codes.OK

        salve.logger.debug(
            '{0}: {1}: Checking source is readable, "{2}"'
            .format(self.file_context, self.prettyname, self.src))

        if not filesys.access(self.src, access_codes.R_OK):
            return self.verification_codes.UNREADABLE_SOURCE

        return self.verification_codes.OK

    def execute(self, filesys):
        """
        FileCopyAction execution.

        Does a file copy or symlink creation, depending on the type
        of the source file.
        """
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('{0}: Performing File Copy "{1}" -> "{2}"'
                          .format(self.file_context, self.src, self.dst))

        filesys.copy(self.src, self.dst)
