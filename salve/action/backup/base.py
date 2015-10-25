import abc
import os

from salve import paths, with_metaclass
from salve.action.copy import CopyAction

from salve.context import ExecutionContext


class BackupAction(with_metaclass(abc.ABCMeta, CopyAction)):
    """
    The base class for all BackupActions, all of which are types of
    CopyActions.

    A BackupAction takes a file to backup, a backup directory and
    logfile, and performs the mechanics of a backup operation.
    """
    def __init__(self, src, file_context):
        """
        BackupAction constructor.

        Args:
            @src
            The file to back up.
            @file_context
            The FileContext.
        """
        backup_dir = os.path.normpath(ExecutionContext()['backup_dir'])
        backup_log = os.path.normpath(ExecutionContext()['backup_log'])
        # in the default case, a Backup is a File Copy into the
        # backup_dir in which the target filename is @src's abspath
        # this leads to bad behavior if run as-is, but can serve as a
        # useful basis for the actual BackupAction
        CopyAction.__init__(self,
                            src,
                            paths.pjoin(backup_dir, 'files'),
                            file_context)
        # although redundant with CopyAction, useful for pretty printing
        self.backup_dir = backup_dir
        # backup_log is a clunky name internally, since we know this is
        # a BackupAction
        self.logfile = backup_log
