#!/usr/bin/python

import abc, os, shutil

import src.execute.action as action
import src.util.locations as locations

class CreateAction(action.Action):
    """
    The base class for all CreateActions.

    A generic Copy takes a destination path, and creates a file or
    directory at that destination.
    The meanings of a Create vary between files and directories, so
    this is an ABC.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, dst, context):
        """
        CreateAction constructor.

        Args:
            @dst
            The destination path (being copied to).
            @context
            The StreamContext of origin.
        """
        action.Action.__init__(self, context)
        self.dst = dst

class FileCreateAction(CreateAction):
    """
    An action to create a single file.
    """
    def __init__(self, dst, context):
        """
        FileCreateAction constructor.

        Args:
            @dst
            Destination path.
            @context
            StreamContext of action origin.
        """
        CreateAction.__init__(self,dst,context)

    def __str__(self):
        return "FileCreateAction(src="+str(self.src)+",dst="+\
               str(self.dst)+",context="+str(self.context)+")"

    def execute(self):
        """
        FileCreateAction execution.

        Does a file creation if the file does not exist.
        """
        def writable_target():
            """
            Checks if the target is in a writable directory.
            """
            return os.access(os.path.dirname(self.dst),os.W_OK)

        if not writable_target(): return

        if not os.path.exists(self.dst):
            with open(self.dst,'w') as f: pass

class DirCreateAction(CreateAction):
    """
    An action to create a directory.
    """
    def __init__(self, dst, context):
        """
        DirCreateAction constructor.

        Args:
            @dst
            Destination path.
            @context
            StreamContext of action origin.
        """
        CreateAction.__init__(self,dst,context)

    def __str__(self):
        return "DirCreateAction(dst="+str(self.dst)+",context="+\
               str(self.context)+")"

    def execute(self):
        """
        Create a directory and any necessary parents.
        """
        def writable_target():
            """
            Checks if the target is in a writable directory.
            """
            ancestor = locations.get_existing_prefix(self.dst)
            return os.access(ancestor,os.W_OK)

        if not writable_target(): return

        # have to invoke this check because makedirs fails if the leaf
        # at the destination exists
        if not os.path.exists(self.dst):
            os.makedirs(self.dst)
