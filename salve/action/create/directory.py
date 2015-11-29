import salve
from salve.action.create.base import CreateAction

from salve.context import ExecutionContext


class DirCreateAction(CreateAction):
    """
    An action to create a directory.
    """
    def execute(self, filesys):
        """
        Create a directory and any necessary parents.
        """
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('{0}: Performing Directory Creation of "{1}"'
                          .format(self.file_context, self.dst))

        # make the directory
        filesys.mkdir(self.dst)
