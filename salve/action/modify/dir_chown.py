from salve import logger, paths, ugo
from salve.action.modify.chown import ChownAction
from salve.action.modify.file_chown import FileChownAction
from salve.action.modify.directory import DirModifyAction
from salve.filesys import access_codes
from salve.context import ExecutionContext


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
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        logger.info('DirChown: Checking target exists, \"%s\"' %
                    self.target, min_verbosity=3)

        if not filesys.access(self.target, access_codes.F_OK):
            return self.verification_codes.NONEXISTENT_TARGET

        logger.info('DirChown: Checking if execution can be skipped, ' +
                    '\"%s\"' % self.target, min_verbosity=3)

        if filesys.stat(self.target).st_uid == ugo.name_to_uid(self.user) and \
           filesys.stat(self.target).st_gid == ugo.name_to_gid(self.group):
            return self.verification_codes.SKIP_EXEC

        logger.info('DirChown: Checking if user is root',
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
            logger.warn(logstr)
            return
        if vcode == self.verification_codes.NOT_ROOT:
            logstr = "DirChown: Cannot Chown as Non-Root User"
            logger.warn(logstr)
            return

        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        logger.info('Performing DirChown of \"%s\" to %s:%s' %
                    (self.target, self.user, self.group),
                    min_verbosity=1)

        if vcode != self.verification_codes.SKIP_EXEC:
            uid = ugo.name_to_uid(self.user)
            gid = ugo.name_to_gid(self.group)
            # chown without following symlinks
            filesys.chown(self.target, uid, gid)

        if self.recursive:
            for directory, subdirs, files in filesys.walk(self.target):
                # chown on all subdirectories
                for sd in subdirs:
                    target = paths.pjoin(directory, sd)
                    # synthesize a new action and invoke it
                    synth = DirChownAction(target,
                                           self.user,
                                           self.group,
                                           self.file_context,
                                           recursive=False)
                    synth(filesys)
                # chown on all files in the directory
                for f in files:
                    target = paths.pjoin(directory, f)
                    # synthesize a new action and invoke it
                    synth = FileChownAction(target,
                                            self.user,
                                            self.group,
                                            self.file_context)
                    synth(filesys)
