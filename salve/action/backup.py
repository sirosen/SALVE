#!/usr/bin/python

from __future__ import print_function

import abc
import time

import salve
from salve.filesys import access_codes

from salve import action
from salve.action import copy

from salve.util import locations
from salve.util import streams
from salve.util.context import ExecutionContext
from salve.util.six import with_metaclass


class BackupAction(with_metaclass(abc.ABCMeta, copy.CopyAction)):
    """
    The base class for all BackupActions, all of which are types of
    CopyActions.

    A BackupAction takes a file to backup, a backup directory and
    logfile, and performs the mechanics of a backup operation.
    """
    def __init__(self, src, file_context):
        """
        BackupAction constructor.

        Args:
            @src
            The file to back up.
            @file_context
            The FileContext.
        """
        backup_dir = salve.exec_context.get('backup_dir')
        backup_log = salve.exec_context.get('backup_log')
        # in the default case, a Backup is a File Copy into the
        # backup_dir in which the target filename is @src's abspath
        # this leads to bad behavior if run as-is, but can serve as a
        # useful basis for the actual BackupAction
        copy.CopyAction.__init__(self,
                                 src,
                                 locations.pjoin(backup_dir, 'files'),
                                 file_context)
        # although redundant with CopyAction, useful for pretty printing
        self.backup_dir = backup_dir
        # backup_log is a clunky name internally, since we know this is
        # a BackupAction
        self.logfile = backup_log


class FileBackupAction(BackupAction, copy.FileCopyAction):
    """
    A single file Backupaction. This is a type of BackupAction, and
    therefore a CopyAction, but more specifically a FileCopyAction.
    """
    verification_codes = \
        copy.FileCopyAction.verification_codes.extend('NONEXISTENT_SOURCE')

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
        salve.exec_context.transition(ExecutionContext.phases.VERIFICATION)

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

        salve.logger.info('FileBackup: Checking source existence, \"%s\"' %
                self.src, file_context=self.file_context,
                min_verbosity=3)

        if not existent_source():
            return self.verification_codes.NONEXISTENT_SOURCE

        salve.logger.info('FileBackup: Checking source is readable, \"%s\"' %
                self.src, file_context=self.file_context,
                min_verbosity=3)

        if not readable_source():
            return self.verification_codes.UNREADABLE_SOURCE

        salve.logger.info('FileBackup: Checking destination is writable, ' +
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
            salve.logger.warn(logstr, file_context=self.file_context)
            return
        if vcode == self.verification_codes.NONEXISTENT_SOURCE:
            logstr = "FileBackup: Non-Existent source file \"%s\"" % self.src
            salve.logger.warn(logstr, file_context=self.file_context)
            return
        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            logstr = "FileBackup: Non-Writable target dir \"%s\"" % self.dst
            salve.logger.warn(logstr, file_context=self.file_context)
            return

        # transition to the execution phase
        salve.exec_context.transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing File Backup of \"%s\"' % self.src,
                file_context=self.file_context, min_verbosity=1)

        filesys.mkdir(self.dst)

        self.hash_val = streams.hash_by_filename(self.src)

        # update dst so that the FileCopyAction can run correctly
        self.dst = locations.pjoin(self.dst, self.hash_val)

        # if the backup exists, no need to actually rewrite it
        if not filesys.exists(self.dst):
            # otherwise, invoke the FileCopyAction execution
            copy.FileCopyAction.execute(self, filesys)

        self.write_log()

    def write_log(self):
        """
        Log the date, hash, and filename, to the backup log.
        """
        logval = time.strftime('%Y-%m-%d %H:%M:%S') + ' ' + \
                 self.hash_val + ' ' + \
                 locations.clean_path(self.src, absolute=True)
        # TODO: use some locks to make this thread-safe for future
        # versions of SALVE supporting parallelism
        with open(self.logfile, 'a') as f:
            print(logval, file=f)


class DirBackupAction(action.ActionList, BackupAction):
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
        action.ActionList.__init__(self, [], file_context)

    def verify_can_exec(self, filesys):
        # transition to the action verification phase,
        # confirming execution will work
        salve.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        salve.logger.info('DirBackup: Checking destination is writable, ' +
                '\"%s\"' % self.dst, file_context=self.file_context,
                min_verbosity=3)

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
            salve.logger.warn(logstr, file_context=self.file_context)
            return

        # transition to the execution phase
        salve.exec_context.transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing Directory Backup of \"%s\"' % self.src,
                file_context=self.file_context, min_verbosity=1)

        # append a file backup for each file in @src
        for dirname, subdirs, files in filesys.walk(self.src):
            # for now, to keep it super-simple, we ignore empty dirs
            for f in files:
                filename = locations.pjoin(dirname, f)
                self.append(FileBackupAction(filename,
                                             self.file_context))

        action.ActionList.execute(self, filesys)
