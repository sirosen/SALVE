import salve
from salve import paths
from salve.action.copy.base import CopyAction
from salve.filesys import access_codes
from salve.context import ExecutionContext


class DirCopyAction(CopyAction):
    def get_verification_code(self, filesys):
        """
        Ensures that the the target directory is writable.
        """
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        salve.logger.debug(
            '{0}: {1}: Checking source is readable + traversable, {2}'
            .format(self.file_context, self.prettyname, self.dst))

        if not filesys.access(self.src, access_codes.R_OK | access_codes.X_OK):
            return self.verification_codes.UNREADABLE_SOURCE

        salve.logger.debug(
            '{0}: {1}: Checking target is writeable, "{2}"'
            .format(self.file_context, self.prettyname, self.dst))

        if not filesys.access(paths.dirname(self.dst), access_codes.W_OK):
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def execute(self, filesys):
        """
        Copy a directory tree from one location to another.
        """
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('{0}: Performing Directory Copy "{1}" -> "{2}"'
                          .format(self.file_context, self.src, self.dst))

        filesys.copy(self.src, self.dst)
