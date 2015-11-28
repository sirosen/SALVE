import salve
from salve.action.create.base import CreateAction

from salve.context import ExecutionContext


class DirCreateAction(CreateAction):
    """
    An action to create a directory.
    """
    def __str__(self):
        return ("DirCreateAction(dst=" + self.dst + ",context=" +
                repr(self.file_context) + ")")

    def verify_can_exec(self, filesys):
        """
        Checks if the target dir already exists, or if its parent is writable.
        """
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        salve.logger.info('{0}: DirCreate: Checking if target exists, "{1}"'
                          .format(self.file_context, self.dst))

        # creation of existing dirs is always OK
        if filesys.exists(self.dst):
            return self.verification_codes.OK

        salve.logger.info('{0}: DirCreate: Checking target is writable, "{1}"'
                          .format(self.file_context, self.dst))

        if not filesys.writable_path_or_ancestor(self.dst):
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def execute(self, filesys):
        """
        Create a directory and any necessary parents.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            salve.logger.warn('{0}: DirCreate: Non-Writable target dir "{1}"'
                              .format(self.file_context, self.dst))
            return

        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('{0}: Performing Directory Creation of "{1}"'
                          .format(self.file_context, self.dst))

        # make the directory
        filesys.mkdir(self.dst)
