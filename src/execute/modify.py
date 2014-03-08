#!/usr/bin/python

from __future__ import print_function

import abc
import os
import sys
import shutil

import src.execute.action as action
import src.util.ugo as ugo
from src.util.context import ExecutionContext

class ModifyAction(action.Action):
    """
    The base class for all Actions that modify existing files and
    directories.
    """
    __metaclass__ = abc.ABCMeta
    verification_codes = \
        action.Action.verification_codes.extend('NONEXISTENT_TARGET')

    def __init__(self, target, context):
        """
        ModifyAction constructor.

        Args:
            @target
            The path to the file or dir to modify.
            @context
            The SALVECOntext.
        """
        action.Action.__init__(self, context)
        self.target = target

class DirModifyAction(ModifyAction):
    """
    The base class for Modify Actions on directories.
    Primarily used to carry information about the recursivity of the
    modification.
    Is an ABC.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, target, recursive, context):
        """
        DirModifyAction constructor.

        Args:
            @target
            Path to the dir to modify.
            @recursive
            If true, apply the modification to any contained files and
            dirs.
            @context
            The SALVEContext.
        """
        ModifyAction.__init__(self,target,context)
        self.recursive = recursive

class ChownAction(ModifyAction):
    """
    The base class for ChownActions.
    Is an ABC.
    """
    __metaclass__ = abc.ABCMeta
    verification_codes = \
        ModifyAction.verification_codes.extend('NOT_ROOT',
                                               'SKIP_EXEC')

    def __init__(self, target, user, group, context):
        """
        ChownAction constructor.

        Args:
            @target
            Path to the dir or file to modify.
            @user
            The new user of @target.
            @group
            The new group of @target.
            @context
            The SALVEContext.
        """
        ModifyAction.__init__(self,target,context)
        self.user = user
        self.group = group

    def verify_can_exec(self):
        # transition to the action verification phase,
        # confirming execution will work
        self.context.transition(ExecutionContext.phases.VERIFICATION)

        if not os.path.exists(self.target):
            return self.verification_codes.NONEXISTENT_TARGET

        # if the chown would do nothing, give skip exec
        if ugo.name_to_uid(self.user) == os.stat(self.target).st_gid and \
           ugo.name_to_gid(self.group) == os.stat(self.target).st_gid:
            return self.verification_codes.SKIP_EXEC

        if not ugo.is_root():
            return self.verification_codes.NOT_ROOT

        return self.verification_codes.OK

class ChmodAction(ModifyAction):
    """
    The base class for ChmodActions.
    Is an ABC.
    """
    __metaclass__ = abc.ABCMeta
    verification_codes = \
        ModifyAction.verification_codes.extend('UNOWNED_TARGET')

    def __init__(self, target, mode, context):
        """
        ChmodAction constructor.

        Args:
            @target
            Path to the dir or file to modify.
            @mode
            The new umask of @target.
            @context
            The SALVEContext.
        """
        ModifyAction.__init__(self,target,context)
        self.mode = int(mode,8)

    def verify_can_exec(self):
        # transition to the action verification phase,
        # confirming execution will work
        self.context.transition(ExecutionContext.phases.VERIFICATION)

        # a nonexistent file or dir can never be chmoded
        if not os.path.exists(self.target):
            return self.verification_codes.NONEXISTENT_TARGET

        # as root, you can always perform a chmod on existing files
        if ugo.is_root():
            return self.verification_codes.OK

        # now the file is known to exist and the user is not root
        if not ugo.is_owner(self.target):
            return self.verification_codes.UNOWNED_TARGET

        return self.verification_codes.OK

class FileChownAction(ChownAction):
    """
    A ChownAction applied to a single file.
    """
    def __init__(self, target, user, group, context):
        """
        FileChownAction constructor.

        Args:
            @target
            Path to the file to chown.
            @user
            The new user of @target.
            @group
            The new group of @target.
            @context
            The SALVEContext.
        """
        ChownAction.__init__(self,target,user,group,context)

    def __str__(self):
        return "FileChownAction(target="+str(self.target)+\
               ",user="+str(self.user)+",group="+str(self.group)+\
               ",context="+str(self.context)+")"

    def execute(self):
        """
        FileChownAction execution.

        Change the owner and group of a single file.
        """
        vcode = self.verify_can_exec()

        if vcode == self.verification_codes.NONEXISTENT_TARGET:
            print((str(self.context)+\
                ": FileChownWarning: Non-Existent target file \"%s\"") % \
                self.target,file=sys.stderr)
            return
        if vcode == self.verification_codes.NOT_ROOT:
            print(str(self.context)+\
                ": FileChownWarning: Cannot Chown as Non-Root User",
                file=sys.stderr)
            return
        # if verification says that we skip without performing any action
        # then there should be no warning message
        if vcode == self.verification_codes.SKIP_EXEC:
            return

        # transition to the execution phase
        self.context.transition(ExecutionContext.phases.EXECUTION)

        # chown without following symlinks
        # lchown works on non-symlink files as well
        os.lchown(self.target,ugo.name_to_uid(self.user),
                  ugo.name_to_gid(self.group))

class FileChmodAction(ChmodAction):
    """
    A ChmodAction applied to a single file.
    """
    def __init__(self, target, mode, context):
        """
        FileChmodAction constructor.

        Args:
            @target
            Path to the file to chmod.
            @mode
            The new umask of @target.
            @context
            The SALVEContext.
        """
        ChmodAction.__init__(self,target,mode,context)

    def __str__(self):
        return "FileChmodAction(target="+str(self.target)+\
               ",mode="+'{0:o}'.format(self.mode)+\
               ",context="+str(self.context)+")"

    def execute(self):
        """
        FileChmodAction execution.

        Change the umask of a single file.
        """
        vcode = self.verify_can_exec()

        if vcode == self.verification_codes.NONEXISTENT_TARGET:
            print((str(self.context)+\
                ": FileChmodWarning: Non-Existent target file \"%s\"") % \
                self.target,file=sys.stderr)
            return
        if vcode == self.verification_codes.UNOWNED_TARGET:
            print((str(self.context)+\
                ": FileChmodWarning: Unowned target file \"%s\"") % \
                self.target,file=sys.stderr)
            return

        # transition to the execution phase
        self.context.transition(ExecutionContext.phases.EXECUTION)

        os.chmod(self.target,self.mode)

class DirChownAction(ChownAction,DirModifyAction):
    """
    A ChownAction applied to a directory.
    """
    def __init__(self, target, user, group, context,
                 recursive=False):
        """
        DirChownAction constructor.

        Args:
            @target
            Path to the dir to chown.
            @user
            The new user of @target.
            @group
            The new group of @target.
            @context
            The SALVEContext.

        KWArgs:
            @recursive
            When True, applies the Chown to all subdirectories and
            contained files. When False, only applies to the root dir.
        """
        DirModifyAction.__init__(self,target,recursive,context)
        ChownAction.__init__(self,target,user,group,context)
        self.recursive = recursive

    def __str__(self):
        return "DirChownAction(target="+str(self.target)+\
               ",user="+str(self.user)+",group="+str(self.group)+\
               ",recursive="+str(self.recursive)+\
               ",context="+str(self.context)+")"

    def verify_can_exec(self):
        # transition to the action verification phase,
        # confirming execution will work
        self.context.transition(ExecutionContext.phases.VERIFICATION)

        if not os.access(self.target,os.F_OK):
            return self.verification_codes.NONEXISTENT_TARGET

        if os.stat(self.target).st_uid == ugo.name_to_uid(self.user) and \
            os.stat(self.target).st_gid == ugo.name_to_gid(self.group):
            return self.verification_codes.SKIP_EXEC

        if not ugo.is_root():
            return self.verification_codes.NOT_ROOT

        return self.verification_codes.OK

    def execute(self):
        """
        DirChownAction execution.

        Change the owner and group of a directory or directory tree.
        """
        vcode = self.verify_can_exec()

        if vcode == self.verification_codes.NONEXISTENT_TARGET:
            print((str(self.context)+\
                ": DirChownWarning: Non-Existent target dir \"%s\"") % \
                self.target,file=sys.stderr)
            return
        if vcode == self.verification_codes.NOT_ROOT:
            print(str(self.context)+\
                ": DirChownWarning: Cannot Chown as Non-Root User",
                file=sys.stderr)
            return

        if vcode != self.verification_codes.SKIP_EXEC:
            uid = ugo.name_to_uid(self.user)
            gid = ugo.name_to_gid(self.group)
            # chown without following symlinks
            os.lchown(self.target,uid,gid)

        # transition to the execution phase
        self.context.transition(ExecutionContext.phases.EXECUTION)

        if self.recursive:
            for directory,subdirs,files in os.walk(self.target):
                # chown on all subdirectories
                for sd in subdirs:
                    target = os.path.join(directory,sd)
                    # synthesize a new action and invoke it
                    synth = DirChownAction(target,
                                           self.user,
                                           self.group,
                                           self.context,
                                           recursive=False)
                    synth()
                # chown on all files in the directory
                for f in files:
                    target = os.path.join(directory,f)
                    # synthesize a new action and invoke it
                    synth = FileChownAction(target,
                                            self.user,
                                            self.group,
                                            self.context)
                    synth()

class DirChmodAction(ChmodAction,DirModifyAction):
    """
    A ChmodAction applied to a directory.
    """
    def __init__(self, target, mode, context, recursive=False):
        """
        DirChmodAction constructor.

        Args:
            @target
            Path to the dir to chown.
            @mode
            The new umask of @target.
            @context
            The SALVEContext.

        KWArgs:
            @recursive
            When True, applies the chmod to all subdirectories and
            contained files. When False, only applies to the root dir.
        """
        DirModifyAction.__init__(self,target,recursive,context)
        ChmodAction.__init__(self,target,mode,context)
        self.recursive = recursive

    def __str__(self):
        return "DirChmodAction(target="+str(self.target)+\
               ",mode="+'{0:o}'.format(self.mode)+\
               ",recursive="+str(self.recursive)+\
               ",context="+str(self.context)+")"

    def verify_can_exec(self):
        # transition to the action verification phase,
        # confirming execution will work
        self.context.transition(ExecutionContext.phases.VERIFICATION)

        if not os.access(self.target,os.F_OK):
            return self.verification_codes.NONEXISTENT_TARGET

        if ugo.is_root():
            return self.verification_codes.OK

        if not ugo.is_owner(self.target):
            return self.verification_codes.UNOWNED_TARGET

        return self.verification_codes.OK

    def execute(self):
        """
        DirChmodAction execution.

        Change the umask of a directory or directory tree.
        """
        vcode = self.verify_can_exec()

        if vcode == self.verification_codes.NONEXISTENT_TARGET:
            print((str(self.context)+\
                ": DirChmodWarning: Non-Existent target dir \"%s\"") % \
                self.target,file=sys.stderr)
            return

        if vcode == self.verification_codes.UNOWNED_TARGET:
            print((str(self.context)+\
                ": DirChmodWarning: Unowned target dir \"%s\"") % \
                self.target,file=sys.stderr)
            return

        # transition to the execution phase
        self.context.transition(ExecutionContext.phases.EXECUTION)

        os.chmod(self.target,self.mode)

        if self.recursive:
            for directory,subdirs,files in os.walk(self.target):
                # chmod on all subdirectories
                for sd in subdirs:
                    target = os.path.join(directory,sd)
                    # synthesize a new action and invoke it
                    # synthetic DirChmods are always nonrecursive
                    synth = DirChmodAction(target,
                                           '{0:o}'.format(self.mode),
                                           self.context,
                                           recursive=False)
                    synth()
                # chmod on all files in the directory
                for f in files:
                    target = os.path.join(directory,f)
                    # synthesize a new action and invoke it
                    synth = FileChmodAction(target,
                                            '{0:o}'.format(self.mode),
                                            self.context)
                    synth()
