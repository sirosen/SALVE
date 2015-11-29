import abc
import os

import salve
from salve import paths, with_metaclass
from salve.action.copy import CopyAction
from salve.filesys import access_codes
from salve.context import ExecutionContext


class BackupAction(with_metaclass(abc.ABCMeta, CopyAction)):
    """
    The base class for all BackupActions, all of which are types of
    CopyActions.

    A BackupAction takes a file to backup, a backup directory and
    logfile, and performs the mechanics of a backup operation.
    """
    verification_codes = (CopyAction.verification_codes
                          .extend('NONEXISTENT_SOURCE'))

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
        CopyAction.__init__(self, src, paths.pjoin(backup_dir, 'files'),
                            file_context)
        # although redundant with CopyAction, useful for pretty printing
        self.backup_dir = backup_dir
        # backup_log is a clunky name internally, since we know this is
        # a BackupAction
        self.logfile = backup_log

    def __str__(self):
        return '{0}(src={1},backup_dir={2},backup_log={3},context={4})'.format(
            self.prettyname, self.src, self.backup_dir, self.logfile,
            self.file_context)

    def get_verification_code(self, filesys):
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        salve.logger.debug(
            '{0}: {1}: Checking source existence, "{2}"'
            .format(self.file_context, self.prettyname, self.src))

        if not filesys.exists(self.src):
            return self.verification_codes.NONEXISTENT_SOURCE

        salve.logger.debug(
            '{0}: {1}: Checking source is readable, "{2}"'
            .format(self.file_context, self.prettyname, self.src))

        if not filesys.access(self.src, access_codes.R_OK):
            return self.verification_codes.UNREADABLE_SOURCE

        salve.logger.debug(
            '{0}: {1}: Checking destination is writable, "{2}"'
            .format(self.file_context, self.prettyname, self.dst))

        if not filesys.writable_path_or_ancestor(self.dst):
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def canexec_non_ok_code(self, code):
        if code is self.verification_codes.UNREADABLE_SOURCE:
            salve.logger.warn(
                '{0}: {1}: Non-Readable source "{2}"'
                .format(self.file_context, self.prettyname, self.src))
            return False
        elif code is self.verification_codes.NONEXISTENT_SOURCE:
            salve.logger.warn(
                '{0}: {1}: Non-Existent source "{2}"'
                .format(self.file_context, self.prettyname, self.src))
            return False
        elif code is self.verification_codes.UNWRITABLE_TARGET:
            salve.logger.warn(
                '{0}: {1}: Non-Writable target dir "{2}"'
                .format(self.file_context, self.prettyname, self.dst))
            return False
