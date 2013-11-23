#!/usr/bin/python

from __future__ import print_function
import abc, os, shutil, hashlib, time

import src.execute.action as action
import src.util.streams

class BackupAction(action.Action):
    __metaclass__ = abc.ABCMeta

    def __init__(self, src, backup_dir, backup_log):
        self.src = src
        self.dst = os.path.join(backup_dir,src.lstrip('/'))
        self.log = backup_log

class FileBackupAction(BackupAction):
    def __init__(self, src, backup_dir, backup_log):
        BackupAction.__init__(self,src,backup_dir,backup_log)

    def execute(self):
        # this has a race condition, but it will only be tripped if
        # another program is writing to the backup dir
        # also, there's no problem with extra invocations of makedirs
        if not os.path.exists(self.dst): os.makedirs(self.dst)

        link_contents = None # unusued unless the file is a link
        if os.path.islink(self.src):
            link_contents = os.readlink(self.src)
            self.hash_val = hashlib.sha256(link_contents).hexdigest()
        else:
            with open(self.src) as f:
                self.hash_val = src.util.streams.sha_512(f)

        target_name = os.path.join(self.dst,self.hash_val)

        # if the backup exists, no need to actually rewrite it
        if not os.path.exists(target_name):
            if os.path.islink(self.src):
                os.symlink(link_contents,target_name)
            else:
                shutil.copyfile(self.src,target_name)

        self.write_log()

    def write_log(self):
        # log the date, filename, to the backup log
        logval = time.strftime('%Y-%m-%d.%s') + ' ' + self.hash_val + ' ' +\
                 self.src
        with open(self.log,'a') as f:
            print(logval,file=f)

class DirBackupAction(action.ActionList,BackupAction):
    def __init__(self, src, backup_dir, backup_log):
        BackupAction.__init__(self,src,backup_dir,backup_log)

        subactions = []
        # for now, to keep it super-simple, we ignore empty dirs
        for dirname,subdirs,files in os.walk(src):
            for f in files:
                filename = os.path.join(dirname,f)
                subactions.append(FileBackupAction(filename,backup_dir,backup_log))

        action.ActionList.__init__(self,subactions)

    def execute(self):
        action.ActionList.execute(self)
