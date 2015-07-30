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
        # transition to the action verification phase,
        # confirming execution will work
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        def writable_target():
            """
            Checks if the backup target dir is writable.
            """
            if filesys.access(self.dst, access_codes.W_OK):
                return True

            if filesys.access(self.dst, access_codes.F_OK):
                return False  # pragma: no cover

            # at this point, the dir is known not to exist
            # now check properties of the containing dir
            containing_dir = filesys.get_existing_ancestor(self.dst)
            if filesys.access(containing_dir, access_codes.W_OK):
                return True

            # if the dir doesn't exist, and the dir containing it
            # isn't writable, then the dir can't be written
            return False

        def existent_source():
            return filesys.access(self.src, access_codes.F_OK)

        def readable_source():
            """
            Checks if the source is a readable file.
            """
            return filesys.access(self.src, access_codes.R_OK)

        logger.info('FileBackup: Checking source existence, \"%s\"' %
                    self.src, file_context=self.file_context,
                    min_verbosity=3)

        if not existent_source():
            return self.verification_codes.NONEXISTENT_SOURCE

        logger.info('FileBackup: Checking source is readable, \"%s\"' %
                    self.src, file_context=self.file_context,
                    min_verbosity=3)

        if not readable_source():
            return self.verification_codes.UNREADABLE_SOURCE

        logger.info('FileBackup: Checking destination is writable, ' +
                    '\"%s\"' % self.dst, file_context=self.file_context,
                    min_verbosity=3)

        if not writable_target():
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
            logger.warn(logstr, file_context=self.file_context)
            return
        if vcode == self.verification_codes.NONEXISTENT_SOURCE:
            logstr = "FileBackup: Non-Existent source file \"%s\"" % self.src
            logger.warn(logstr, file_context=self.file_context)
            return
        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            logstr = "FileBackup: Non-Writable target dir \"%s\"" % self.dst
            logger.warn(logstr, file_context=self.file_context)
            return

        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        logger.info('Performing File Backup of \"%s\"' % self.src,
                    file_context=self.file_context, min_verbosity=1)

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
