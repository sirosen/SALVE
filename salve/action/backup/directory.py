from salve import logger, paths
from salve.action.list import ActionList
from salve.action.backup.base import BackupAction
from salve.action.backup.file import FileBackupAction

from salve.context import ExecutionContext


class DirBackupAction(ActionList, BackupAction):
    """
    A single dir Backupaction. This is a type of BackupAction, and
    therefore a CopyAction, but also an AL of file backups.
    """
    verification_codes = \
        BackupAction.verification_codes.extend('NONEXISTENT_SOURCE')

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

    def verify_can_exec(self, filesys):
        # transition to the action verification phase,
        # confirming execution will work
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        logger.info(
            '{0}: DirBackup: Checking destination is writable, \"{1}\"'.format(
                self.file_context, self.dst)
            )

        if not filesys.exists(self.src):
            return self.verification_codes.NONEXISTENT_SOURCE

        return self.verification_codes.OK

    def execute(self, filesys):
        """
        Execute the DirBackupAction.

        Consists of an AL execution of all file backups.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.NONEXISTENT_SOURCE:
            logstr = "DirBackup: Non-Existent source dir \"%s\"" % self.src
            logger.warn('{0}: {1}'.format(self.file_context, logstr))
            return

        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        logger.info(
            '{0}: Performing Directory Backup of \"{1}\"'.format(
                self.file_context, self.src)
            )

        # append a file backup for each file in @src
        for dirname, subdirs, files in filesys.walk(self.src):
            # for now, to keep it super-simple, we ignore empty dirs
            for f in files:
                filename = paths.pjoin(dirname, f)
                self.append(FileBackupAction(filename, self.file_context))

        ActionList.execute(self, filesys)
