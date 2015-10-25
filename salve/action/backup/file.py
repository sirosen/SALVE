from __future__ import print_function

import time

from salve import logger, paths
from salve.action.backup.base import BackupAction
from salve.action.copy import FileCopyAction

from salve.filesys import access_codes
from salve.context import ExecutionContext
from salve.util import hash_from_path


class FileBackupAction(BackupAction, FileCopyAction):
    """
    A single file Backupaction. This is a type of BackupAction, and
    therefore a CopyAction, but more specifically a FileCopyAction.
    """
    verification_codes = \
        FileCopyAction.verification_codes.extend('NONEXISTENT_SOURCE')

    def __init__(self, src, file_context):
        """
        FileBackupAction constructor.

        Args:
            @src
            The source file.
            @file_context
            The FileContext.
        """
        # initialize as a BackupAction with a destination in the @backup_dir
        # should include initialization as a CopyAction
        BackupAction.__init__(self, src, file_context)
        # the hash_val is the result of taking the sha hash of @src
        self.hash_val = None

    def __str__(self):
        return ("FileBackupAction(src=" + self.src + ",backup_dir=" +
                self.backup_dir + ",backup_log=" + self.logfile +
                ",context=" + str(self.file_context) + ")")

    def verify_can_exec(self, filesys):
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        logger.info(
            '{0}: FileBackup: Checking source existence, \"{1}\"'.format(
                str(self.file_context), self.src)
            )

        if not filesys.exists(self.src):
            return self.verification_codes.NONEXISTENT_SOURCE

        logger.info(
            '{0}: FileBackup: Checking source is readable, \"{1}\"'.format(
                str(self.file_context), self.src)
            )

        if not filesys.access(self.src, access_codes.R_OK):
            return self.verification_codes.UNREADABLE_SOURCE

        logger.info(
            ('{0}: FileBackup: Checking destination ' +
             'is writable, \"{1}\"').format(
                str(self.file_context), self.dst)
            )

        if not filesys.writable_path_or_ancestor(self.dst):
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def execute(self, filesys):
        """
        Perform the FileBackupAction.

        Rewrites dst based on the value of the @src, does a file copy,
        then writes to the logfile.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.UNREADABLE_SOURCE:
            logstr = "FileBackup: Non-Readable source file \"%s\"" % self.src
            logger.warn('{0}: {1}'.format(self.file_context, logstr))
            return
        if vcode == self.verification_codes.NONEXISTENT_SOURCE:
            logstr = "FileBackup: Non-Existent source file \"%s\"" % self.src
            logger.warn('{0}: {1}'.format(self.file_context, logstr))
            return
        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            logstr = "FileBackup: Non-Writable target dir \"%s\"" % self.dst
            logger.warn('{0}: {1}'.format(self.file_context, logstr))
            return

        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        logger.info(
            '{0}: Performing File Backup of \"{1}\"'.format(
                str(self.file_context), self.src)
            )

        filesys.mkdir(self.dst)

        self.hash_val = hash_from_path(self.src)

        # update dst so that the FileCopyAction can run correctly
        self.dst = paths.pjoin(self.dst, self.hash_val)

        # if the backup exists, no need to actually rewrite it
        if not filesys.exists(self.dst):
            # otherwise, invoke the FileCopyAction execution
            FileCopyAction.execute(self, filesys)

        self.write_log()

    def write_log(self):
        """
        Log the date, hash, and filename, to the backup log.
        """
        logval = time.strftime('%Y-%m-%d %H:%M:%S') + ' ' + \
            self.hash_val + ' ' + \
            paths.clean_path(self.src, absolute=True)
        # TODO: use some locks to make this thread-safe for future
        # versions of SALVE supporting parallelism
        with open(self.logfile, 'a') as f:
            print(logval, file=f)
