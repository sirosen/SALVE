import salve
from salve import paths, ugo
from salve.action.modify.chown import ChownAction
from salve.action.modify.file_chown import FileChownAction
from salve.action.modify.directory import DirModifyAction
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
        return (('{0}(target={1},user={2},group={3},recursive={4},'
                 'context={5!r})')
                .format(self.prettyname, self.target, self.user, self.group,
                        self.recursive, self.file_context))

    def _execute_on_contents(self, filesys):
        """
        Recursive execution on directory contents.
        """
        for directory, subdirs, files in filesys.walk(self.target):
            # chown on all subdirectories
            for sd in subdirs:
                # synthesize a new action and invoke it
                synth = DirChownAction(paths.pjoin(directory, sd), self.user,
                                       self.group, self.file_context)
                synth(filesys)
            # chown on all files in the directory
            for f in files:
                # synthesize a new action and invoke it
                synth = FileChownAction(paths.pjoin(directory, f), self.user,
                                        self.group, self.file_context)
                synth(filesys)

    def execute(self, filesys):
        """
        DirChownAction execution.

        Change the owner and group of a directory or directory tree.
        """
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing DirChown of "{0}" to {1}:{2}'
                          .format(self.target, self.user, self.group))

        # chown without following symlinks
        filesys.chown(self.target, ugo.name_to_uid(self.user),
                      ugo.name_to_gid(self.group))

        if self.recursive:
            self._execute_on_contents(filesys)
