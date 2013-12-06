#!/usr/bin/python

from __future__ import print_function
import abc, os, shutil, hashlib, time

import src.execute.action as action
import src.execute.copy as copy
import src.util.streams

class BackupAction(copy.CopyAction):
    __metaclass__ = abc.ABCMeta

    def __init__(self, src, backup_dir, backup_log, context):
        copy.CopyAction.__init__(self,
                                 src,
                                 os.path.join(backup_dir,
                                              os.path.relpath(src,'/')),
                                 context)
        self.logfile = backup_log

class FileBackupAction(BackupAction,copy.FileCopyAction):
    def __init__(self, src, backup_dir, backup_log, context):
        BackupAction.__init__(self,src,backup_dir,backup_log,context)
        self.hash_val = None

    def __str__(self):
        return "FileBackupAction(src="+self.src+",backup_dir="+\
               self.backup_dir+",backup_log="+self.logfile+\
               ",context="+str(self.context)+")"

    def execute(self):
        # no-op if the file to back up does not exist
        if not os.path.exists(self.src): return

        # ensure (up to a reasonable doubt) that the dir exists
        # there's no problem with extra invocations of makedirs
        if not os.path.exists(self.dst): os.makedirs(self.dst)

        if os.path.islink(self.src):
            link_contents = os.readlink(self.src)
            self.hash_val = hashlib.sha256(link_contents).hexdigest()
        else:
            with open(self.src) as f:
                self.hash_val = src.util.streams.sha_512(f)

        # update dst so that the FileCopyAction can run correctly
        self.dst = os.path.join(self.dst,self.hash_val)

        # if the backup exists, no need to actually rewrite it
        if not os.path.exists(self.dst):
            # otherwise, invoke the FileCopyAction execution
            copy.FileCopyAction.execute(self)

        self.write_log()

    def write_log(self):
        # log the date, filename, to the backup log
        logval = time.strftime('%Y-%m-%d.%s') + ' ' + self.hash_val + ' ' +\
                 self.src
        with open(self.logfile,'a') as f:
            print(logval,file=f)

class DirBackupAction(action.ActionList,BackupAction):
    def __init__(self, src, backup_dir, backup_log, context):
        BackupAction.__init__(self,src,backup_dir,backup_log,context)
        action.ActionList.__init__(self,[],context)

        # for now, to keep it super-simple, we ignore empty dirs
        for dirname,subdirs,files in os.walk(src):
            for f in files:
                filename = os.path.join(dirname,f)
                self.append(FileBackupAction(filename,backup_dir,backup_log,context))

    def execute(self):
        action.ActionList.execute(self)
