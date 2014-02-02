#!/usr/bin/python

from __future__ import print_function

import abc
import os
import shutil

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
    verification_codes = \
        action.Action.verification_codes.extend('UNWRITABLE_TARGET')

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
        return "FileCreateAction(dst="+str(self.dst)+\
            ",context="+str(self.context)+")"

    def verify_can_exec(self):
        """
        Ensures that the target file exists and is writable, or that
        it does not exist and is in a writable directory.
        """
        def writable_target():
            """
            Checks if the target is in a writable directory.
            """
            if os.access(self.dst,os.W_OK):
                return True
            if os.access(self.dst,os.F_OK):
                return False
            # file is now known not to exist

            if os.access(os.path.dirname(self.dst),os.W_OK):
                return True

            # the file is doesn't exist and the containing dir is
            # not writable or doesn't exist
            return False

        if not writable_target():
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def execute(self):
        """
        FileCreateAction execution.

        Does a file creation if the file does not exist.
        """
        vcode = self.verify_can_exec()

        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            print((str(self.context)+": FileCreateWarning: Non-Writable target file \"%s\"") % \
                self.dst,file=sys.stderr)
            return

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

    def verify_can_exec(self):
        """
        Checks if the target dir already exists, or if its parent is writable.
        """
        def writable_target():
            """
            Checks if the target is in a writable directory.
            """
            ancestor = locations.get_existing_prefix(self.dst)
            return os.access(ancestor,os.W_OK)

        # creation of existing dirs is always OK
        if os.path.exists(self.dst):
            return self.verification_codes.OK

        if not writable_target():
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def execute(self):
        """
        Create a directory and any necessary parents.
        """
        vcode = self.verify_can_exec()

        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            print((str(self.context)+ \
                  ": DirCreateWarning: Non-Writable target dir \"%s\"") % \
                self.dst,file=sys.stderr)
            return

        # have to invoke this check because makedirs fails if the leaf
        # at the destination exists
        if not os.path.exists(self.dst):
            os.makedirs(self.dst)
