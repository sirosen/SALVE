import salve
from salve.action.create.base import CreateAction

from salve.context import ExecutionContext


class FileCreateAction(CreateAction):
    """
    An action to create a single file.
    """
    def execute(self, filesys):
        """
        FileCreateAction execution.

        Does a file creation if the file does not exist.
        """
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('{0}: Performing File Creation of "{1}"'
                          .format(self.file_context, self.dst))

        # touch the file
        filesys.touch(self.dst)
