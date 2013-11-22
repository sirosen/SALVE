#!/usr/bin/python

import abc, os, shutil

import src.execute.action as action
import src.util.streams

class BackupAction(action.Action):
    __metaclass__ = abc.ABCMeta

    def __init__(self, src, backup_dir):
        self.src = src
        self.dst = os.path.join(backup_dir,src.lstrip('/'))

class FileBackupAction(BackupAction):
    def __init__(self, src, backup_dir):
        BackupAction.__init__(self,src,backup_dir)

    def execute(self):
        target_name = None
        with open(self.src) as f:
            target_name = src.util.streams.sha_512(f)
        target_name = os.path.join(self.dst,target_name)

        # this has a race condition, but it will only be tripped if
        # another program is writing to the backup dir
        if not os.path.exists(self.dst): os.makedirs(self.dst)
        if not os.path.exists(target_name):
            if os.path.islink(self.src):
                os.symlink(os.readlink(self.src),target_name)
            else:
                shutil.copyfile(self.src,target_name)

class DirBackupAction(action.ActionList,BackupAction):
    def __init__(self, src, backup_dir):
        BackupAction.__init__(self,src,backup_dir)

        subactions = []
        # for now, to keep it super-simple, we ignore empty dirs
        for dirname,subdirs,files in os.walk(src):
            for f in files:
                filename = os.path.join(dirname,f)
                subactions.append(FileBackupAction(filename,backup_dir))

        action.ActionList.__init__(self,subactions)

    def execute(self):
        action.ActionList.execute(self)
