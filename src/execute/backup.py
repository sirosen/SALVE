#!/usr/bin/python

from __future__ import print_function

import abc
import os
import sys
import time

import src.execute.action as action
import src.execute.copy as copy
import src.util.locations as locations
import src.util.streams

import src.util.log as log
from src.util.context import ExecutionContext

class BackupAction(copy.CopyAction):
    """
    The base class for all BackupActions, all of which are types of
    CopyActions.

    A BackupAction takes a file to backup, a backup directory and
    logfile, and performs the mechanics of a backup operation.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, src, context):
        """
        BackupAction constructor.

        Args:
            @src
            The file to back up.
            @context
            The SALVEContext.
        """
        backup_dir = context.exec_context.get('backup_dir')
        backup_log = context.exec_context.get('backup_log')
        # in the default case, a Backup is a File Copy into the
        # backup_dir in which the target filename is @src's abspath
        # this leads to bad behavior if run as-is, but can serve as a
        # useful basis for the actual BackupAction
        copy.CopyAction.__init__(self,
                                 src,
                                 os.path.join(backup_dir,'files'),
                                 context)
        # although redundant with CopyAction, useful for pretty printing
        self.backup_dir = backup_dir
        # backup_log is a clunky name internally, since we know this is
        # a BackupAction
        self.logfile = backup_log

class FileBackupAction(BackupAction,copy.FileCopyAction):
    """
    A single file Backupaction. This is a type of BackupAction, and
    therefore a CopyAction, but more specifically a FileCopyAction.
    """
    verification_codes = \
        copy.FileCopyAction.verification_codes.extend('NONEXISTENT_SOURCE')

    def __init__(self, src, context):
        """
        FileBackupAction constructor.

        Args:
            @src
            The source file.
            @context
            The SALVEContext.
        """
        # initialize as a BackupAction with a destination in the @backup_dir
        # should include initialization as a CopyAction
        BackupAction.__init__(self,src,context)
        # the hash_val is the result of taking the sha hash of @src
        self.hash_val = None

    def __str__(self):
        return "FileBackupAction(src="+self.src+",backup_dir="+\
               self.backup_dir+",backup_log="+self.logfile+\
               ",context="+str(self.context)+")"

    def verify_can_exec(self):
        # transition to the action verification phase,
        # confirming execution will work
        self.context.transition(ExecutionContext.phases.VERIFICATION)

        def writable_target():
            """
            Checks if the backup target dir is writable.
            """
            if os.access(self.dst,os.W_OK):
                return True

            if os.access(self.dst,os.F_OK):
                return False

            # at this point, the dir is known not to exist
            # now check properties of the containing dir
            containing_dir = locations.get_existing_prefix(self.dst)
            if os.access(containing_dir,os.W_OK):
                return True

            # if the dir doesn't exist, and the dir containing it
            # isn't writable, then the dir can't be written
            return False

        def existant_source():
            return os.access(self.src,os.F_OK)

        def readable_source():
            """
            Checks if the source is a readable file.
            """
            return os.access(self.src,os.R_OK)

        log.info('FileBackup: Checking source existence, \"%s\"' % self.src,
                 self.context,min_verbosity=3)

        if not existant_source():
            return self.verification_codes.NONEXISTENT_SOURCE

        log.info('FileBackup: Checking source is readable, \"%s\"' % self.src,
                 self.context,min_verbosity=3)

        if not readable_source():
            return self.verification_codes.UNREADABLE_SOURCE

        log.info('FileBackup: Checking destination is writable, \"%s\"' % self.dst,
                 self.context,min_verbosity=3)

        if not writable_target():
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def execute(self):
        """
        Perform the FileBackupAction.

        Rewrites dst based on the value of the @src, does a file copy,
        then writes to the logfile.
        """
        vcode = self.verify_can_exec()

        if vcode == self.verification_codes.UNREADABLE_SOURCE:
            logstr = "FileBackup: Non-Readable source file \"%s\"" % self.src
            log.warn(logstr,self.context)
            return
        if vcode == self.verification_codes.NONEXISTENT_SOURCE:
            logstr = "FileBackup: Non-Existent source file \"%s\"" % self.src
            log.warn(logstr,self.context)
            return
        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            logstr = "FileBackup: Non-Writable target dir \"%s\"" % self.dst
            log.warn(logstr,self.context)
            return

        # transition to the execution phase
        self.context.transition(ExecutionContext.phases.EXECUTION)

        log.info('Performing File Backup of \"%s\"' % self.src,self.context,min_verbosity=1)

        # FIXME: change to EAFP style
        if not os.path.exists(self.dst): os.makedirs(self.dst)

        self.hash_val = src.util.streams.hash_by_filename(self.src)

        # update dst so that the FileCopyAction can run correctly
        self.dst = os.path.join(self.dst,self.hash_val)

        # if the backup exists, no need to actually rewrite it
        if not os.path.exists(self.dst):
            # otherwise, invoke the FileCopyAction execution
            copy.FileCopyAction.execute(self)

        self.write_log()

    def write_log(self):
        """
        Log the date, hash, and filename, to the backup log.
        """
        logval = time.strftime('%Y-%m-%d %H:%M:%S') + ' ' + \
                 self.hash_val + ' ' + \
                 locations.clean_path(self.src,absolute=True)
        # TODO: use some locks to make this thread-safe for future
        # versions of SALVE supporting parallelism
        with open(self.logfile,'a') as f:
            print(logval,file=f)

class DirBackupAction(action.ActionList,BackupAction):
    """
    A single dir Backupaction. This is a type of BackupAction, and
    therefore a CopyAction, but also an AL of file backups.
    """
    verification_codes = \
        BackupAction.verification_codes.extend('NONEXISTENT_SOURCE')

    def __init__(self, src, context):
        """
        DirBackupAction constructor.

        Args:
            @src
            The dir to back up.
            @context
            The SALVEContext.
        """
        # call both parent constructors so that all fields are in place
        # don't use super because it complicates argument passing
        BackupAction.__init__(self,src,context)
        action.ActionList.__init__(self,[],context)

    def verify_can_exec(self):
        # transition to the action verification phase,
        # confirming execution will work
        self.context.transition(ExecutionContext.phases.VERIFICATION)

        log.info('DirBackup: Checking destination is writable, \"%s\"' % self.dst,
                 self.context,min_verbosity=3)

        if not os.path.exists(self.src):
            return self.verification_codes.NONEXISTENT_SOURCE

        return self.verification_codes.OK

    def execute(self):
        """
        Execute the DirBackupAction.

        Consists of an AL execution of all file backups.
        """
        vcode = self.verify_can_exec()

        if vcode == self.verification_codes.NONEXISTENT_SOURCE:
            logstr = "DirBackup: Non-Existent source dir \"%s\"" % self.src
            log.warn(logstr,self.context)
            return

        # transition to the execution phase
        self.context.transition(ExecutionContext.phases.EXECUTION)

        log.info('Performing Directory Backup of \"%s\"' % self.src,self.context,min_verbosity=1)

        # append a file backup for each file in @src
        for dirname,subdirs,files in os.walk(self.src):
            # for now, to keep it super-simple, we ignore empty dirs
            for f in files:
                filename = os.path.join(dirname,f)
                self.append(FileBackupAction(filename,
                                             self.context))

        action.ActionList.execute(self)
