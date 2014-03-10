#!/usr/bin/python

import sys
import abc
import os
import shutil

import src.execute.action as action
import src.util.enum as enum

import src.util.log as log
from src.util.context import ExecutionContext

class CopyAction(action.Action):
    """
    The base class for all CopyActions.

    A generic Copy takes a source and destination, and copies the
    source to the destination. The meanings of a Copy vary between
    files and directories, so this is an ABC.
    """
    __metaclass__ = abc.ABCMeta
    verification_codes = \
        action.Action.verification_codes.extend('UNWRITABLE_TARGET')

    def __init__(self, src, dst, context):
        """
        CopyAction constructor.

        Args:
            @src
            The source path (file being copied).
            @dst
            The destination path (being copied to).
            @context
            The SALVEContext.
        """
        action.Action.__init__(self,context)
        self.src = src
        self.dst = dst

class FileCopyAction(CopyAction):
    """
    An action to copy a single file.
    """
    verification_codes = \
        CopyAction.verification_codes.extend('UNREADABLE_SOURCE')

    def __init__(self, src, dst, context):
        """
        FileCopyAction constructor.

        Args:
            @src
            Source path.
            @dst
            Destination path.
            @context
            The SALVEContext.
        """
        CopyAction.__init__(self,src,dst,context)

    def __str__(self):
        """
        Stringification into type, source, dst, and context.
        """
        return "FileCopyAction(src="+str(self.src)+",dst="+\
               str(self.dst)+",context="+str(self.context)+")"

    def verify_can_exec(self):
        """
        Check to ensure that execution can proceed without errors.
        Ensures that the source file exists and is readable, and that
        the target file can be created or is writable.
        """
        # transition to the action verification phase,
        # confirming execution will work
        self.context.transition(ExecutionContext.phases.VERIFICATION)

        def writable_target():
            """
            Checks if the target file is writable.
            """
            if os.access(self.dst,os.W_OK):
                return True
            if os.access(self.dst,os.F_OK):
                return False

            # at this point, the file is known not to exist
            # now check properties of the containing dir
            containing_dir = os.path.dirname(self.dst)
            if os.access(containing_dir,os.W_OK):
                return True

            # if the file doesn't exist, and the dir containing it
            # isn't writable, then the file can't be written
            return False

        def readable_source():
            """
            Checks if the source is a readable file.
            """
            return os.access(self.src,os.R_OK)

        log.info('FileCopy: Checking destination is writable, \"%s\"' % self.dst,
                 self.context,min_verbosity=3)

        if not writable_target():
            return self.verification_codes.UNWRITABLE_TARGET

        log.info('FileCopy: Checking source is readable, \"%s\"' % self.src,
                 self.context,min_verbosity=3)

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
            logstr = "FileCopy: Non-Writable target file \"%s\"" % self.dst
            log.warn(logstr,self.context)
            return

        if vcode == self.verification_codes.UNREADABLE_SOURCE:
            logstr = "FileCopy: Non-Readable source file \"%s\"" % self.src
            log.warn(logstr,self.context)
            return

        # transition to the execution phase
        self.context.transition(ExecutionContext.phases.EXECUTION)

        log.info('Performing File Copy \"%s\" -> \"%s\"' % (self.src,self.dst),
                 self.context,min_verbosity=1)

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
            The SALVEContext.
        """
        CopyAction.__init__(self,src,dst,context)

    def __str__(self):
        return "DirCopyAction(src="+str(self.src)+",dst="+\
               str(self.dst)+",context="+str(self.context)+")"

    def verify_can_exec(self):
        """
        Check to ensure that execution can proceed without errors.
        Ensures that the the target directory is writable.
        """
        # transition to the action verification phase,
        # confirming execution will work
        self.context.transition(ExecutionContext.phases.VERIFICATION)

        def writable_target():
            """
            Checks if the target is in a writable directory.
            """
            return os.access(os.path.dirname(self.dst),os.W_OK)

        log.info('DirCopy: Checking target is writable, \"%s\"' % self.dst,
                 self.context,min_verbosity=3)

        if not writable_target():
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def execute(self):
        """
        Copy a directory tree from one location to another.
        """
        vcode = self.verify_can_exec()

        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            logstr = "DirCopy: Non-Writable target directory \"%s\"" % self.dst
            log.warn(logstr,self.context)
            return

        # transition to the execution phase
        self.context.transition(ExecutionContext.phases.EXECUTION)

        log.info('Performing Directory Copy \"%s\" -> \"%s\"' % (self.src,self.dst),
                 self.context,min_verbosity=1)

        shutil.copytree(self.src,self.dst,symlinks=True)
