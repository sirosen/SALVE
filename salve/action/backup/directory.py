import salve
from salve import paths
from salve.action.list import ActionList
from salve.action.backup.base import BackupAction
from salve.action.backup.file import FileBackupAction

from salve.context import ExecutionContext


class DirBackupAction(ActionList, BackupAction):
    """
    A single dir Backupaction. This is a type of BackupAction, and
    therefore a CopyAction, but also an AL of file backups.
    """
    verification_codes = BackupAction.verification_codes

    def __init__(self, src, file_context):
        """
        DirBackupAction constructor.

        Args:
            @src
            The dir to back up.
            @file_context
            The FileContext.
        """
        # call both parent constructors so that all fields are in place
        # don't use super because it complicates argument passing
        BackupAction.__init__(self, src, file_context)
        ActionList.__init__(self, [], file_context)

    def execute(self, filesys):
        """
        Execute the DirBackupAction.

        Consists of an AL execution of all file backups.
        """
        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info(
            '{0}: Performing Directory Backup of "{1}"'
            .format(self.file_context, self.src))

        # append a file backup for each file in @src
        for dirname, subdirs, files in filesys.walk(self.src):
            # for now, to keep it super-simple, we ignore empty dirs
            for f in files:
                filename = paths.pjoin(dirname, f)
                self.append(FileBackupAction(filename, self.file_context))

        ActionList.execute(self, filesys)
