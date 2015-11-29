import salve
from salve import paths
from salve.action.modify.chmod import ChmodAction
from salve.action.modify.file_chmod import FileChmodAction
from salve.action.modify.directory import DirModifyAction

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
        return '{0}(target={1},mode={2:o},recursive={3},context={4!r})'.format(
            self.prettyname, self.target, self.mode, self.recursive,
            self.file_context)

    def execute(self, filesys):
        """
        DirChmodAction execution.

        Change the umask of a directory or directory tree.
        """
        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing DirChmod of "{0}" to {1:o}'
                          .format(self.target, self.mode))

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
