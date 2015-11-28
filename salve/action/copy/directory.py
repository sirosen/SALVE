import salve
from salve import paths
from salve.action.copy.base import CopyAction
from salve.filesys import access_codes
from salve.context import ExecutionContext


class DirCopyAction(CopyAction):
    def verify_can_exec(self, filesys):
        """
        Check to ensure that execution can proceed without errors.
        Ensures that the the target directory is writable.
        """
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        salve.logger.info(
            '{0}: DirCopy: Checking source is readable + traversable, {1}'
            .format(self.file_context, self.dst))

        if not filesys.access(self.src, access_codes.R_OK | access_codes.X_OK):
            return self.verification_codes.UNREADABLE_SOURCE

        salve.logger.info('{0}: DirCopy: Checking target is writeable, "{1}"'
                          .format(self.file_context, self.dst))

        if not filesys.access(paths.dirname(self.dst), access_codes.W_OK):
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def execute(self, filesys):
        """
        Copy a directory tree from one location to another.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.UNREADABLE_SOURCE:
            salve.logger.warn(
                '{0}: DirCopy: Non-Readable source directory "{1}"'
                .format(self.file_context, self.src))
            return

        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            salve.logger.warn(
                '{0}: DirCopy: Non-Writable target directory "{1}"'
                .format(self.file_context, self.dst))
            return

        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('{0}: Performing Directory Copy "{1}" -> "{2}"'
                          .format(self.file_context, self.src, self.dst))

        filesys.copy(self.src, self.dst)
