#!/usr/bin/python

import abc

import salve

from salve import action
from salve.filesys import access_codes
from salve.util import locations
from salve.util import ugo
from salve.util.context import ExecutionContext
from salve.util.six import with_metaclass


class ModifyAction(with_metaclass(abc.ABCMeta, action.Action)):
    """
    The base class for all Actions that modify existing files and
    directories.
    """
    verification_codes = \
        action.Action.verification_codes.extend('NONEXISTENT_TARGET')

    def __init__(self, target, file_context):
        """
        ModifyAction constructor.

        Args:
            @target
            The path to the file or dir to modify.
            @file_context
            The SALVECOntext.
        """
        action.Action.__init__(self, file_context)
        self.target = target


class DirModifyAction(with_metaclass(abc.ABCMeta, ModifyAction)):
    """
    The base class for Modify Actions on directories.
    Primarily used to carry information about the recursivity of the
    modification.
    Is an ABC.
    """
    def __init__(self, target, recursive, file_context):
        """
        DirModifyAction constructor.

        Args:
            @target
            Path to the dir to modify.
            @recursive
            If true, apply the modification to any contained files and
            dirs.
            @file_context
            The FileContext.
        """
        ModifyAction.__init__(self, target, file_context)
        self.recursive = recursive


class ChownAction(with_metaclass(abc.ABCMeta, ModifyAction)):
    """
    The base class for ChownActions.
    Is an ABC.
    """
    verification_codes = \
        ModifyAction.verification_codes.extend('NOT_ROOT',
                                               'SKIP_EXEC')

    def __init__(self, target, user, group, file_context):
        """
        ChownAction constructor.

        Args:
            @target
            Path to the dir or file to modify.
            @user
            The new user of @target.
            @group
            The new group of @target.
            @file_context
            The FileContext.
        """
        ModifyAction.__init__(self, target, file_context)
        self.user = user
        self.group = group

    def verify_can_exec(self, filesys):
        # transition to the action verification phase,
        # confirming execution will work
        salve.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        salve.logger.info('Chown: Checking target exists, \"%s\"' %
                self.target, min_verbosity=3)

        if not filesys.exists(self.target):
            return self.verification_codes.NONEXISTENT_TARGET

        salve.logger.info('Chown: Checking if execution can be skipped, ' +
                '\"%s\"' % self.target, min_verbosity=3)

        # if the chown would do nothing, give skip exec
        if ugo.name_to_uid(self.user) == filesys.stat(self.target).st_uid and \
           ugo.name_to_gid(self.group) == filesys.stat(self.target).st_gid:
            return self.verification_codes.SKIP_EXEC

        salve.logger.info('Chown: Checking user is root', min_verbosity=3)

        if not ugo.is_root():
            return self.verification_codes.NOT_ROOT

        return self.verification_codes.OK


class ChmodAction(with_metaclass(abc.ABCMeta, ModifyAction)):
    """
    The base class for ChmodActions.
    Is an ABC.
    """
    verification_codes = \
        ModifyAction.verification_codes.extend('UNOWNED_TARGET')

    def __init__(self, target, mode, file_context):
        """
        ChmodAction constructor.

        Args:
            @target
            Path to the dir or file to modify.
            @mode
            The new umask of @target.
            @file_context
            The FileContext.
        """
        ModifyAction.__init__(self, target, file_context)
        self.mode = int(mode, 8)

    def verify_can_exec(self, filesys):
        # transition to the action verification phase,
        # confirming execution will work
        salve.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        salve.logger.info('Chmod: Checking target exists, \"%s\"' %
                self.target, min_verbosity=3)

        # a nonexistent file or dir can never be chmoded
        if not filesys.exists(self.target):
            return self.verification_codes.NONEXISTENT_TARGET

        salve.logger.info('Chmod: Checking if user is root', min_verbosity=3)

        # as root, you can always perform a chmod on existing files
        if ugo.is_root():
            return self.verification_codes.OK

        salve.logger.info('Chmod: Checking if user is owner of target, ' +
                '\"%s\"' % self.target, min_verbosity=3)

        # now the file is known to exist and the user is not root
        if not ugo.is_owner(self.target):
            return self.verification_codes.UNOWNED_TARGET

        return self.verification_codes.OK


class FileChownAction(ChownAction):
    """
    A ChownAction applied to a single file.
    """
    def __init__(self, target, user, group, file_context):
        """
        FileChownAction constructor.

        Args:
            @target
            Path to the file to chown.
            @user
            The new user of @target.
            @group
            The new group of @target.
            @file_context
            The FileContext.
        """
        ChownAction.__init__(self, target, user, group, file_context)

    def __str__(self):
        return ("FileChownAction(target=" + str(self.target) +
                ",user=" + str(self.user) + ",group=" + str(self.group) +
                ",context=" + repr(self.file_context) + ")")

    def execute(self, filesys):
        """
        FileChownAction execution.

        Change the owner and group of a single file.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.NONEXISTENT_TARGET:
            logstr = "FileChown: Non-Existent target file \"%s\"" % self.target
            salve.logger.warn(logstr)
            return
        if vcode == self.verification_codes.NOT_ROOT:
            logstr = "FileChown: Cannot Chown as Non-Root User"
            salve.logger.warn(logstr)
            return
        # if verification says that we skip without performing any action
        # then there should be no warning message
        if vcode == self.verification_codes.SKIP_EXEC:
            return

        # transition to the execution phase
        salve.exec_context.transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing FileChown of \"%s\" to %s:%s' %
            (self.target, self.user, self.group), min_verbosity=1)

        # chown without following symlinks
        filesys.chown(self.target, ugo.name_to_uid(self.user),
                  ugo.name_to_gid(self.group))


class FileChmodAction(ChmodAction):
    """
    A ChmodAction applied to a single file.
    """
    def __init__(self, target, mode, file_context):
        """
        FileChmodAction constructor.

        Args:
            @target
            Path to the file to chmod.
            @mode
            The new umask of @target.
            @file_context
            The FileContext.
        """
        ChmodAction.__init__(self, target, mode, file_context)

    def __str__(self):
        return ("FileChmodAction(target=" + str(self.target) +
                ",mode=" + '{0:o}'.format(self.mode) +
                ",context=" + repr(self.file_context) + ")")

    def execute(self, filesys):
        """
        FileChmodAction execution.

        Change the umask of a single file.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.NONEXISTENT_TARGET:
            logstr = "FileChmod: Non-Existent target file \"%s\"" % self.target
            salve.logger.warn(logstr)
            return
        if vcode == self.verification_codes.UNOWNED_TARGET:
            logstr = "FileChmod: Unowned target file \"%s\"" % self.target
            salve.logger.warn(logstr)
            return

        # transition to the execution phase
        salve.exec_context.transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing FileChmod of \"%s\" to %s' %
            (self.target, '{0:o}'.format(self.mode)), min_verbosity=1)

        filesys.chmod(self.target, self.mode)


class DirChownAction(ChownAction, DirModifyAction):
    """
    A ChownAction applied to a directory.
    """
    def __init__(self, target, user, group, file_context,
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
            @file_context
            The FileContext.

        KWArgs:
            @recursive
            When True, applies the Chown to all subdirectories and
            contained files. When False, only applies to the root dir.
        """
        DirModifyAction.__init__(self, target, recursive, file_context)
        ChownAction.__init__(self, target, user, group, file_context)
        self.recursive = recursive

    def __str__(self):
        return ("DirChownAction(target=" + str(self.target) +
                ",user=" + str(self.user) + ",group=" + str(self.group) +
                ",recursive=" + str(self.recursive) +
                ",context=" + repr(self.file_context) + ")")

    def verify_can_exec(self, filesys):
        # transition to the action verification phase,
        # confirming execution will work
        salve.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        salve.logger.info('DirChown: Checking target exists, \"%s\"' %
                self.target, min_verbosity=3)

        if not filesys.access(self.target, access_codes.F_OK):
            return self.verification_codes.NONEXISTENT_TARGET

        salve.logger.info('DirChown: Checking if execution can be skipped, ' +
                '\"%s\"' % self.target, min_verbosity=3)

        if filesys.stat(self.target).st_uid == ugo.name_to_uid(self.user) and \
            filesys.stat(self.target).st_gid == ugo.name_to_gid(self.group):
            return self.verification_codes.SKIP_EXEC

        salve.logger.info('DirChown: Checking if user is root',
                min_verbosity=3)

        if not ugo.is_root():
            return self.verification_codes.NOT_ROOT

        return self.verification_codes.OK

    def execute(self, filesys):
        """
        DirChownAction execution.

        Change the owner and group of a directory or directory tree.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.NONEXISTENT_TARGET:
            logstr = "DirChown: Non-Existent target dir \"%s\"" % self.target
            salve.logger.warn(logstr)
            return
        if vcode == self.verification_codes.NOT_ROOT:
            logstr = "DirChown: Cannot Chown as Non-Root User"
            salve.logger.warn(logstr)
            return

        # transition to the execution phase
        salve.exec_context.transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing DirChown of \"%s\" to %s:%s' %
            (self.target, self.user, self.group), min_verbosity=1)

        if vcode != self.verification_codes.SKIP_EXEC:
            uid = ugo.name_to_uid(self.user)
            gid = ugo.name_to_gid(self.group)
            # chown without following symlinks
            filesys.chown(self.target, uid, gid)

        if self.recursive:
            for directory, subdirs, files in filesys.walk(self.target):
                # chown on all subdirectories
                for sd in subdirs:
                    target = locations.pjoin(directory, sd)
                    # synthesize a new action and invoke it
                    synth = DirChownAction(target,
                                           self.user,
                                           self.group,
                                           self.file_context,
                                           recursive=False)
                    synth(filesys)
                # chown on all files in the directory
                for f in files:
                    target = locations.pjoin(directory, f)
                    # synthesize a new action and invoke it
                    synth = FileChownAction(target,
                                            self.user,
                                            self.group,
                                            self.file_context)
                    synth(filesys)


class DirChmodAction(ChmodAction, DirModifyAction):
    """
    A ChmodAction applied to a directory.
    """
    def __init__(self, target, mode, file_context, recursive=False):
        """
        DirChmodAction constructor.

        Args:
            @target
            Path to the dir to chown.
            @mode
            The new umask of @target.
            @file_context
            The FileContext.

        KWArgs:
            @recursive
            When True, applies the chmod to all subdirectories and
            contained files. When False, only applies to the root dir.
        """
        DirModifyAction.__init__(self, target, recursive, file_context)
        ChmodAction.__init__(self, target, mode, file_context)
        self.recursive = recursive

    def __str__(self):
        return ("DirChmodAction(target=" + str(self.target) +
                ",mode=" + '{0:o}'.format(self.mode) +
                ",recursive=" + str(self.recursive) +
                ",context=" + repr(self.file_context) + ")")

    def verify_can_exec(self, filesys):
        # transition to the action verification phase,
        # confirming execution will work
        salve.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        salve.logger.info('DirChmod: Checking if target exists, \"%s\"' %
                self.target, min_verbosity=3)

        if not filesys.access(self.target, access_codes.F_OK):
            return self.verification_codes.NONEXISTENT_TARGET

        salve.logger.info('DirChmod: Checking if user is root',
                min_verbosity=3)

        if ugo.is_root():
            return self.verification_codes.OK

        salve.logger.info('DirChmod: Checking if user is target owner, ' +
                '\"%s\"' % self.target, min_verbosity=3)

        if not ugo.is_owner(self.target):
            return self.verification_codes.UNOWNED_TARGET

        return self.verification_codes.OK

    def execute(self, filesys):
        """
        DirChmodAction execution.

        Change the umask of a directory or directory tree.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.NONEXISTENT_TARGET:
            logstr = "DirChmod: Non-Existent target dir \"%s\"" % self.target
            salve.logger.warn(logstr)
            return

        if vcode == self.verification_codes.UNOWNED_TARGET:
            logstr = "DirChmod: Unowned target dir \"%s\"" % self.target
            salve.logger.warn(logstr)
            return

        # transition to the execution phase
        salve.exec_context.transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing DirChmod of \"%s\" to %s' %
            (self.target, '{0:o}'.format(self.mode)), min_verbosity=1)

        filesys.chmod(self.target, self.mode)

        if self.recursive:
            for directory, subdirs, files in filesys.walk(self.target):
                # chmod on all subdirectories
                for sd in subdirs:
                    target = locations.pjoin(directory, sd)
                    # synthesize a new action and invoke it
                    # synthetic DirChmods are always nonrecursive
                    synth = DirChmodAction(target,
                                           '{0:o}'.format(self.mode),
                                           self.file_context,
                                           recursive=False)
                    synth(filesys)
                # chmod on all files in the directory
                for f in files:
                    target = locations.pjoin(directory, f)
                    # synthesize a new action and invoke it
                    synth = FileChmodAction(target,
                                            '{0:o}'.format(self.mode),
                                            self.file_context)
                    synth(filesys)
