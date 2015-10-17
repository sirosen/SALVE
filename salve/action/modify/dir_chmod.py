from salve import logger, paths, ugo
from salve.action.modify.chmod import ChmodAction
from salve.action.modify.file_chmod import FileChmodAction
from salve.action.modify.directory import DirModifyAction

from salve.filesys import access_codes
from salve.context import ExecutionContext


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
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        logger.info('DirChmod: Checking if target exists, \"%s\"' %
                    self.target)

        if not filesys.access(self.target, access_codes.F_OK):
            return self.verification_codes.NONEXISTENT_TARGET

        logger.info('DirChmod: Checking if user is root')

        if ugo.is_root():
            return self.verification_codes.OK

        logger.info('DirChmod: Checking if user is target owner, ' +
                    '\"%s\"' % self.target)

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
            logger.warn(logstr)
            return

        if vcode == self.verification_codes.UNOWNED_TARGET:
            logstr = "DirChmod: Unowned target dir \"%s\"" % self.target
            logger.warn(logstr)
            return

        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        logger.info('Performing DirChmod of \"%s\" to %s' %
                    (self.target, '{0:o}'.format(self.mode)))

        filesys.chmod(self.target, self.mode)

        if self.recursive:
            for directory, subdirs, files in filesys.walk(self.target):
                # chmod on all subdirectories
                for sd in subdirs:
                    target = paths.pjoin(directory, sd)
                    # synthesize a new action and invoke it
                    # synthetic DirChmods are always nonrecursive
                    synth = DirChmodAction(target,
                                           '{0:o}'.format(self.mode),
                                           self.file_context,
                                           recursive=False)
                    synth(filesys)
                # chmod on all files in the directory
                for f in files:
                    target = paths.pjoin(directory, f)
                    # synthesize a new action and invoke it
                    synth = FileChmodAction(target,
                                            '{0:o}'.format(self.mode),
                                            self.file_context)
                    synth(filesys)
