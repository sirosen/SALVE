#!/usr/bin/python

import abc, os, shutil

import src.execute.action as action
import src.util.ugo as ugo

class ModifyAction(action.Action):
    __metaclass__ = abc.ABCMeta

    def __init__(self, target, context):
        action.Action.__init__(self, context)
        self.target = target

    @abc.abstractmethod
    def __str__(self): pass #pragma: no cover

    @abc.abstractmethod
    def execute(self): pass #pragma: no cover

class DirModifyAction(ModifyAction):
    __metaclass__ = abc.ABCMeta

    def __init__(self, target, recursive, context):
        ModifyAction.__init__(self,target,context)
        self.recursive = recursive

class ChownAction(ModifyAction):
    __metaclass__ = abc.ABCMeta

    def __init__(self, target, user, group, context):
        ModifyAction.__init__(self,target,context)
        self.user = user
        self.group = group

    @abc.abstractmethod
    def __str__(self): pass #pragma: no cover

    @abc.abstractmethod
    def execute(self): pass #pragma: no cover

class ChmodAction(ModifyAction):
    __metaclass__ = abc.ABCMeta

    def __init__(self, target, mode, context):
        ModifyAction.__init__(self,target,context)
        self.mode = int(mode,8)

    @abc.abstractmethod
    def __str__(self): pass #pragma: no cover

    @abc.abstractmethod
    def execute(self): pass #pragma: no cover

class FileChownAction(ChownAction):
    def __init__(self, target, user, group, context):
        ChownAction.__init__(self,target,user,group,context)

    def __str__(self):
        return "FileChownAction(target="+str(self.target)+\
               ",user="+str(self.user)+",group="+str(self.group)+\
               ",context="+str(self.context)+")"

    def execute(self):
        # chown without following symlinks
        # lchown works on non-symlink files as well
        os.lchown(self.target,ugo.name_to_uid(self.user),
                  ugo.name_to_gid(self.group))

class FileChmodAction(ChmodAction):
    def __init__(self, target, mode, context):
        ChmodAction.__init__(self,target,mode,context)

    def __str__(self):
        return "FileChmodAction(target="+str(self.target)+\
               ",mode="+'{0:o}'.format(self.mode)+\
               ",context="+str(self.context)+")"

    def execute(self):
        os.chmod(self.target,self.mode)

class DirChownAction(ChownAction,DirModifyAction):
    def __init__(self, target, user, group, context, recursive=False):
        DirModifyAction.__init__(self,target,recursive,context)
        ChownAction.__init__(self,target,user,group,context)
        self.recursive = recursive

    def __str__(self):
        return "DirChownAction(target="+str(self.target)+\
               ",user="+str(self.user)+",group="+str(self.group)+\
               ",recursive="+str(self.recursive)+\
               ",context="+str(self.context)+")"

    def execute(self):
        uid = ugo.name_to_uid(self.user)
        gid = ugo.name_to_gid(self.group)
        os.lchown(self.target,uid,gid)
        if self.recursive:
            for directory,subdirs,files in os.walk(self.target):
                # chown on all subdirectories
                for sd in subdirs:
                    # chown without following symlinks
                    os.lchown(os.path.join(directory,sd),uid,gid)
                # chown on all files in the directory
                for f in files:
                    # chown without following symlinks
                    os.lchown(os.path.join(directory,f),uid,gid)

class DirChmodAction(ChmodAction,DirModifyAction):
    def __init__(self, target, mode, context, recursive=False):
        DirModifyAction.__init__(self,target,recursive,context)
        ChmodAction.__init__(self,target,mode,context)
        self.recursive = recursive

    def __str__(self):
        return "DirChmodAction(target="+str(self.target)+\
               ",mode="+'{0:o}'.format(self.mode)+\
               ",recursive="+str(self.recursive)+\
               ",context="+str(self.context)+")"

    def execute(self):
        os.chmod(self.target,self.mode)
        if self.recursive:
            for directory,subdirs,files in os.walk(self.target):
                # chmod on all subdirectories
                for sd in subdirs:
                    os.chmod(os.path.join(directory,sd),self.mode)
                # chmod on all files in the directory
                for f in files:
                    os.chmod(os.path.join(directory,f),self.mode)
