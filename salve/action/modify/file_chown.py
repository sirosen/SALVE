import salve
from salve import ugo
from salve.action.modify.chown import ChownAction
from salve.context import ExecutionContext


class FileChownAction(ChownAction):
    """
    A ChownAction applied to a single file.
    """
    def __init__(self, target, user, group, file_context):
        """
        FileChownAction constructor.

        Args:
            @target
            Path to the file to chown.
            @user
            The new user of @target.
            @group
            The new group of @target.
            @file_context
            The FileContext.
        """
        ChownAction.__init__(self, target, user, group, file_context)

    def __str__(self):
        return '{0}(target={1},user={2},group={3},context={4!r})'.format(
            self.prettyname, self.target, self.user, self.group,
            self.file_context)

    def execute(self, filesys):
        """
        FileChownAction execution.

        Change the owner and group of a single file.
        """
        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing FileChown of "{0}" to {1}:{2}'
                          .format(self.target, self.user, self.group))

        # chown without following symlinks
        filesys.chown(self.target, ugo.name_to_uid(self.user),
                      ugo.name_to_gid(self.group))
