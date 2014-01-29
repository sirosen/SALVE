#!/usr/bin/python

from __future__ import print_function

import sys
import abc
import os
import shutil

import src.execute.action as action

import src.util.enum as enum

class CopyAction(action.Action):
    """
    The base class for all CopyActions.

    A generic Copy takes a source and destination, and copies the
    source to the destination. The meanings of a Copy vary between
    files and directories, so this is an ABC.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, src, dst, context):
        """
        CopyAction constructor.

        Args:
            @src
            The source path (file being copied).
            @dst
            The destination path (being copied to).
            @context
            The StreamContext of origin.
        """
        action.Action.__init__(self, context)
        self.src = src
        self.dst = dst

class FileCopyAction(CopyAction):
    verification_codes = \
        CopyAction.verification_codes.extend('UNWRITABLE_TARGET',
                                             'UNREADABLE_SOURCE')
    """
    An action to copy a single file.
    """
    def __init__(self, src, dst, context):
        """
        FileCopyAction constructor.

        Args:
            @src
            Source path.
            @dst
            Destination path.
            @context
            StreamContext of action origin.
        """
        CopyAction.__init__(self,src,dst,context)

    def __str__(self):
        """
        Stringification into type, source, dst, and context.
        """
        return "FileCopyAction(src="+str(self.src)+",dst="+\
               str(self.dst)+",context="+str(self.context)+")"

    def verify_can_exec(self):
        def writable_target():
            """
            Checks if the target file is writable.
            """
            try:
                with open(self.dst,'wb') as dst:
                    pass
                return True
            except IOError as e:
                if e.errno == 13:
                    return False
                else:
                    raise e

        def readable_source():
            """
            Checks if the source is a readable file.
            """
            return os.access(self.src,os.R_OK)

        if not writable_target():
            return self.verification_codes.UNWRITABLE_TARGET

        if not readable_source():
            return self.verification_codes.UNREADABLE_SOURCE

        return self.verification_codes.OK

    def execute(self):
        """
        FileCopyAction execution.

        Does a file copy or symlink creation, depending on the type
        of the source file.
        """
        vcode = self.verify_can_exec()

        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            print((str(self.context)+": Warning: Non-Writable target file \"%s\"") % \
                self.dst,file=sys.stderr)
            return

        if vcode == self.verification_codes.UNREADABLE_SOURCE:
            print((str(self.context)+": Warning: Non-Readable source file \"%s\"") % \
                self.src,file=sys.stderr)
            return

        if os.path.islink(self.src):
            os.symlink(os.readlink(self.src),self.dst)
        else:
            shutil.copyfile(self.src,self.dst)

class DirCopyAction(CopyAction):
    """
    An action to copy a directory tree.
    """
    def __init__(self, src, dst, context):
        """
        DirCopyAction constructor.

        Args:
            @src
            Source path.
            @dst
            Destination path.
            @context
            StreamContext of action origin.
        """
        CopyAction.__init__(self,src,dst,context)

    def __str__(self):
        return "DirCopyAction(src="+str(self.src)+",dst="+\
               str(self.dst)+",context="+str(self.context)+")"

    def execute(self):
        """
        Copy a directory tree from one location to another.
        """

        def writable_target():
            """
            Checks if the target is in a writable directory.
            """
            return os.access(os.path.dirname(self.dst),os.W_OK)

        if not writable_target(): return

        shutil.copytree(self.src,self.dst,symlinks=True)
