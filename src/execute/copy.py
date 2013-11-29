#!/usr/bin/python

import abc, os, shutil

import src.execute.action as action
import src.util.ugo as ugo

class CopyAction(action.Action):
    __metaclass__ = abc.ABCMeta

    def __init__(self, src, dst, user, group, mode, context):
        action.Action.__init__(self, context)
        self.src = src
        self.dst = dst
        self.user = user
        self.group = group
        self.mode = int(mode,8)

    @abc.abstractmethod
    def __str__(self): pass #pragma: no cover

    @abc.abstractmethod
    def execute(self): pass #pragma: no cover

class FileCopyAction(CopyAction):
    def __init__(self, src, dst, user, group, mode, context):
        CopyAction.__init__(self,src,dst,user,group,mode,context)

    def __str__(self):
        return "FileCopyAction(src="+str(self.src)+",dst="+\
               str(self.dst)+",user="+str(self.user)+",group="+\
               str(self.group)+",mode="+'{0:o}'.format(self.mode)+\
               ",context="+str(self.context)+")"

    def execute(self):
        shutil.copyfile(self.src,self.dst)
        os.chmod(self.dst,self.mode)
        # if not root, skip attempting chown
        if ugo.is_root():
            # chown without following symlinks
            os.lchown(self.dst,src.util.ugo.name_to_uid(self.user),
                      src.util.ugo.name_to_gid(self.group))

class DirCopyAction(CopyAction):
    def __init__(self, src, dst, user, group, mode, context):
        CopyAction.__init__(self,src,dst,user,group,mode,context)

    def __str__(self):
        return "DirCopyAction(src="+str(self.src)+",dst="+\
               str(self.dst)+",user="+str(self.user)+",group="+\
               str(self.group)+",mode="+'{0:o}'.format(self.mode)+\
               ",context="+str(self.context)+")"

    def execute(self):
        """
        Copy a directory tree from one location to another, and change
        the umask of every file in the tree to self.mode
        """
        shutil.copytree(self.src,self.dst,symlinks=True)
        os.chmod(self.dst,self.mode)
        # assumes that the current process can read and write
        # directories with the set umask
        # it is up to users to make sure this is the case
        # otherwise, there will be no directory traversal and the chmod
        # will have no effect, but also no errors
        for directory,subdirs,files in os.walk(self.dst):
            # chmod on all subdirectories
            for sd in subdirs:
                target = os.path.join(directory,sd)
                os.chmod(target,self.mode)
                if ugo.is_root():
                    # chown without following symlinks
                    os.lchown(target,
                              src.util.ugo.name_to_uid(self.user),
                              src.util.ugo.name_to_gid(self.group))
            # chmod on all files in the directory
            for f in files:
                target = os.path.join(directory,f)
                os.chmod(target,self.mode)
                if ugo.is_root():
                    # chown without following symlinks
                    os.lchown(target,
                              src.util.ugo.name_to_uid(self.user),
                              src.util.ugo.name_to_gid(self.group))
