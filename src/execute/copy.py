#!/usr/bin/python

import abc, os, shutil

import src.execute.action as action
import src.util.ugo as ugo

class CopyAction(action.Action):
    __metaclass__ = abc.ABCMeta

    def __init__(self, src, dst, context):
        action.Action.__init__(self, context)
        self.src = src
        self.dst = dst

    @abc.abstractmethod
    def __str__(self): pass #pragma: no cover

    @abc.abstractmethod
    def execute(self): pass #pragma: no cover

class FileCopyAction(CopyAction):
    def __init__(self, src, dst, context):
        CopyAction.__init__(self,src,dst,context)

    def __str__(self):
        return "FileCopyAction(src="+str(self.src)+",dst="+\
               str(self.dst)+",context="+str(self.context)+")"

    def execute(self):
        shutil.copyfile(self.src,self.dst)

class DirCopyAction(CopyAction):
    def __init__(self, src, dst, context):
        CopyAction.__init__(self,src,dst,context)

    def __str__(self):
        return "DirCopyAction(src="+str(self.src)+",dst="+\
               str(self.dst)+",context="+str(self.context)+")"

    def execute(self):
        """
        Copy a directory tree from one location to another.
        """
        shutil.copytree(self.src,self.dst,symlinks=True)
