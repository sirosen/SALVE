#!/usr/bin/python

import abc, os, shutil

import src.execute.action as action
import src.util.ugo as ugo

class ModifyAction(action.Action):
    """
    The base class for all Actions that modify existing files and
    directories.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, target, context):
        """
        ModifyAction constructor.

        Args:
            @target
            The path to the file or dir to modify.
            @context
            The StreamContext of Action origin.
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
            The StreamContext of Action origin.
        """
        ModifyAction.__init__(self,target,context)
        self.recursive = recursive

class ChownAction(ModifyAction):
    """
    The base class for ChownActions.
    Is an ABC.
    """
    __metaclass__ = abc.ABCMeta

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
            The StreamContext of Action origin.
        """
        ModifyAction.__init__(self,target,context)
        self.user = user
        self.group = group

class ChmodAction(ModifyAction):
    """
    The base class for ChmodActions.
    Is an ABC.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, target, mode, context):
        """
        ChmodAction constructor.

        Args:
            @target
            Path to the dir or file to modify.
            @mode
            The new umask of @target.
            @context
            The StreamContext of Action origin.
        """
        ModifyAction.__init__(self,target,context)
        self.mode = int(mode,8)

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
            The StreamContext of Action origin.
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
            The StreamContext of Action origin.
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
        # skip the chmod if the current user is not the owner or root
        # or the file is missing
        if not (os.access(self.target,os.F_OK) and
                (ugo.is_root() or
                 os.stat(self.target).st_uid == os.getuid())):
            return

        os.chmod(self.target,self.mode)

class DirChownAction(ChownAction,DirModifyAction):
    """
    A ChownAction applied to a directory.
    """
    def __init__(self, target, user, group, context, recursive=False):
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
            The StreamContext of Action origin.

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

    def execute(self):
        """
        DirChownAction execution.

        Change the owner and group of a directory or directory tree.
        """
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
            The StreamContext of Action origin.

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

    def execute(self):
        """
        DirChmodAction execution.

        Change the umask of a directory or directory tree.
        """
        os.chmod(self.target,self.mode)
        if self.recursive:
            for directory,subdirs,files in os.walk(self.target):
                # chmod on all subdirectories
                for sd in subdirs:
                    target = os.path.join(directory,sd)
                    if (ugo.is_root() or
                        os.stat(target).st_uid == os.getuid()):
                        os.chmod(target,self.mode)
                # chmod on all files in the directory
                for f in files:
                    target = os.path.join(directory,f)
                    if (ugo.is_root() or
                        os.stat(target).st_uid == os.getuid()):
                        os.chmod(target,self.mode)
