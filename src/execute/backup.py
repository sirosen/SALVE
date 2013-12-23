#!/usr/bin/python

from __future__ import print_function

import abc
import os
import time

import src.execute.action as action
import src.execute.copy as copy
import src.util.streams

class BackupAction(copy.CopyAction):
    """
    The base class for all BackupActions, all of which are types of
    CopyActions.

    A BackupAction takes a file to backup, a backup directory and
    logfile, and performs the mechanics of a backup operation.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, src, backup_dir, backup_log, context):
        """
        BackupAction constructor.

        Args:
            @src
            The file to back up.
            @backup_dir
            The directory in which @src should be backed up.
            @backup_log
            A logfile, which should have the backup action's details
            appended after execution.
            @context
            The BackupAction's StreamContext of origin.
        """
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
    def __init__(self, src, backup_dir, backup_log, context):
        """
        FileBackupAction constructor.

        Args:
            @src
            The source file.
            @backup_dir
            The storage location for backups.
            @backup_log
            The logfile for backups.
            @context
            The action's originating StreamContext.
        """
        # create the basic action; the only value that needs to be
        # rewriten is the dst
        BackupAction.__init__(self,src,backup_dir,backup_log,context)
        # the hash_val is the result of taking the sha hash of @src
        self.hash_val = None

    def __str__(self):
        return "FileBackupAction(src="+self.src+",backup_dir="+\
               self.backup_dir+",backup_log="+self.logfile+\
               ",context="+str(self.context)+")"

    def execute(self):
        """
        Perform the FileBackupAction.

        Rewrites dst based on the value of the @src, does a file copy,
        then writes to the logfile.
        """
        # no-op if the file to back up does not exist
        if not os.path.exists(self.src): return

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
        logval = time.strftime('%Y-%m-%d.%s') + ' ' + self.hash_val + ' ' +\
                 self.src
        # TODO: use some locks to make this thread-safe for future
        # versions of SALVE supporting parallelism
        with open(self.logfile,'a') as f:
            print(logval,file=f)

class DirBackupAction(action.ActionList,BackupAction):
    """
    A single dir Backupaction. This is a type of BackupAction, and
    therefore a CopyAction, but also an AL of file backups.
    """
    def __init__(self, src, backup_dir, backup_log, context):
        """
        DirBackupAction constructor.

        Args:
            @src
            The dir to back up.
            @backup_dir
            The directory in which @src should be backed up.
            @backup_log
            A logfile, to which each of the backup actions' details will
            be appended after execution.
            @context
            The DirBackupAction's StreamContext of origin.
        """
        # call both parent constructors so that all fields are in place
        # don't use super because it complicates argument passing
        BackupAction.__init__(self,src,backup_dir,backup_log,context)
        action.ActionList.__init__(self,[],context)

        # append a file backup for each file in @src
        for dirname,subdirs,files in os.walk(src):
            # for now, to keep it super-simple, we ignore empty dirs
            for f in files:
                filename = os.path.join(dirname,f)
                self.append(FileBackupAction(filename,backup_dir,backup_log,context))

    def execute(self):
        """
        Execute the DirBackupAction.

        Consists of an AL execution of all file backups.
        """
        action.ActionList.execute(self)
