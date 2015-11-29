import os
import mock

from nose.tools import istest, eq_, ok_
from tests.framework import ensure_except, scratch, full_path, assert_substr
from tests.unit.action import dummy_file_context

from salve import action
from salve.action import backup
from salve.filesys import ConcreteFilesys
from salve.context import ExecutionContext


def patch_filebackup_autoverify_nolog(function):
    return mock.patch.multiple(
        'salve.action.backup.FileBackupAction',
        verify_can_exec=lambda self, fs: self.verification_codes.OK,
        write_log=mock.MagicMock()
    )(function)


class TestWithScratchdir(scratch.ScratchContainer):
    def setUp(self):
        scratch.ScratchContainer.setUp(self)
        ExecutionContext()['run_log'] = self.stderr
        ExecutionContext()['backup_dir'] = '/etc/salve/backup'
        ExecutionContext()['backup_log'] = '/etc/salve/backup.log'

    @istest
    @patch_filebackup_autoverify_nolog
    @mock.patch('salve.filesys.ConcreteFilesys.mkdir')
    @mock.patch('salve.action.copy.FileCopyAction.execute')
    def file_target_name(self, mock_cp, mock_mkdir):
        """
        Unit: File Backup Action Destination File
        Verifies that a file's abspath followed by its SHA512 hash is its
        destination file when backed up.
        """
        self.write_file('file1.txt', 'Hashing target.\n')
        filename = self.get_fullname('file1.txt')

        act = backup.FileBackupAction(filename, dummy_file_context)
        act(ConcreteFilesys())

        mock_mkdir.assert_called_once_with('/etc/salve/backup/files')

        eq_(os.path.basename(act.dst),
            ('9bfabef5ffd7f5df84171393643e7ceeba916e64876ace612ca8d20ad0ff'
             'd69e0ecd284ca7899f4bab6805c06f881296d20f619e714befb255e23fdf'
             '09ef0eed'))

        cp_act = mock_cp.call_args[0][0]
        eq_(cp_act.src, filename)
        eq_(cp_act.dst, act.dst)

    @istest
    @patch_filebackup_autoverify_nolog
    @mock.patch('salve.filesys.ConcreteFilesys.mkdir')
    @mock.patch('salve.action.copy.FileCopyAction.execute')
    def file_symlink_target_name(self, mock_cp, mock_mkdir):
        """
        Unit: File Backup Action Symlink Destination File
        Verifies that a symlink's abspath followed by its SHA256 hash is its
        destination file when backed up.
        """
        linkname = self.get_fullname('file_link1')
        os.symlink('file1.txt', linkname)

        act = backup.FileBackupAction(linkname, dummy_file_context)
        act(ConcreteFilesys())

        mock_mkdir.assert_called_once_with('/etc/salve/backup/files')
        eq_(os.path.basename(act.dst),
            ('55ae75d991c770d8f3ef07cbfde124ffce'
             '9c420da5db6203afab700b27e10cf9'))

        cp_act = mock_cp.call_args[0][0]
        eq_(cp_act.src, linkname)
        eq_(cp_act.dst, act.dst)

    @istest
    def backupaction_is_abstract(self):
        """
        Unit: Backup Action Base Class Is Abstract
        Checks that instantiating a BackupAction raises an error.
        """
        ensure_except(TypeError, backup.BackupAction, '/a/b/c',
                      dummy_file_context)

    @istest
    def file_dst_dir(self):
        """
        Unit: File Backup Action Destination Directory
        Verifies that a file's abspath becomes its storage directory under
        the backup dir.
        """
        filename = full_path('file1.txt')
        act = backup.FileBackupAction(filename, dummy_file_context)
        eq_(act.dst, '/etc/salve/backup/files')

    @istest
    def file_to_str(self):
        """
        Unit: File Backup Action to String

        Checks the result of converting a file backup action to a string.
        """
        filename = full_path('file1.txt')
        act = backup.FileBackupAction(filename, dummy_file_context)
        eq_(str(act),
            ('FileBackupAction(src={0},backup_dir=/etc/salve/backup,'
             'backup_log=/etc/salve/backup.log,context={1})')
            .format(filename, dummy_file_context))

    @istest
    @mock.patch('salve.action.backup.file.print', create=True)
    @mock.patch('salve.action.backup.file.open', create=True)
    def file_write_log(self, mock_open, mock_print):
        """
        Unit: File Backup Action Write Log
        Verifies that on a successful backup action, the logfile is written
        with the date, hash, and filename.
        """
        filename = full_path('file1.txt')
        act = backup.FileBackupAction(filename, dummy_file_context)
        act.hash_val = 'abc'

        with mock.patch('time.strftime', lambda s: 'NOW'):
            act.write_log()

        mock_open.assert_called_once_with('/etc/salve/backup.log', 'a')
        eq_(mock_print.call_args[0][0], ('NOW abc ' + filename))

    @istest
    @mock.patch('salve.action.list.ActionList.execute')
    @mock.patch('salve.action.backup.DirBackupAction.verify_can_exec')
    def dir_expand(self, mock_verify, mock_execute):
        """
        Unit: Directory Backup Action Expand Dir
        Checks the expansion of a directory into its constituent files for
        directory backups.
        """
        mock_verify.return_value = True

        dirname = full_path('dir1')
        act = backup.DirBackupAction(dirname, dummy_file_context)

        act(ConcreteFilesys())

        # must be a valid ActionList
        ok_(isinstance(act, action.ActionList))
        ok_(hasattr(act, 'actions'))
        seen_files = set()
        for subact in act.actions:
            ok_(isinstance(subact, backup.FileBackupAction))
            seen_files.add(subact.src)
        ok_(full_path('dir1/a') in seen_files)
        ok_(full_path('dir1/b') in seen_files)
        ok_(full_path('dir1/inner_dir1/.abc') in seen_files)

    @istest
    @mock.patch('salve.action.backup.FileBackupAction.execute', autospec=True)
    @mock.patch('salve.action.backup.DirBackupAction.verify_can_exec')
    @mock.patch('salve.action.backup.FileBackupAction.verify_can_exec')
    def dir_execute(self, mock_verify1, mock_verify2, mock_execute):
        """
        Unit: Directory Backup Action Execute
        Verifies that executing a DirBackupAction runs a FileBackupAction on
        each of the files in the directory.
        """
        mock_verify1.return_value = mock_verify2.return_value = True

        dirname = full_path('dir1')
        act = backup.DirBackupAction(dirname, dummy_file_context)
        # check this here so that we abort the test if this condition is
        # unsatisfied, rather than starting to actually perform actions
        for subact in act.actions:
            ok_(isinstance(subact, backup.FileBackupAction))

        act(ConcreteFilesys())

        seen_files = [args[0][0].src for args in mock_execute.call_args_list]

        ok_(full_path('dir1/a') in seen_files)
        ok_(full_path('dir1/b') in seen_files)
        ok_(full_path('dir1/inner_dir1/.abc') in seen_files)

    @istest
    def dir_verify_no_source(self):
        """
        Unit: Directory Backup Action Verify (No Source)
        Verifies that verification of a DirBackupAction identifies missing
        source dir.
        """
        dirname = full_path('no such dir')
        act = backup.DirBackupAction(dirname, dummy_file_context)
        # check this here so that we abort the test if this condition is
        # unsatisfied, rather than starting to actually perform actions
        for subact in act.actions:
            ok_(isinstance(subact, backup.FileBackupAction))

        eq_(act.get_verification_code(ConcreteFilesys()),
            backup.DirBackupAction.verification_codes.NONEXISTENT_SOURCE)

    @istest
    def dir_execute_no_source(self):
        """
        Unit: Directory Backup Action Execute (No Source)
        Verifies that verification of a DirBackupAction identifies missing
        source dir during execution.
        """
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION,
                                      quiet=True)

        dirname = full_path('no such dir')
        act = backup.DirBackupAction(dirname, dummy_file_context)
        # check this here so that we abort the test if this condition is
        # unsatisfied, rather than starting to actually perform actions
        for subact in act.actions:
            ok_(isinstance(subact, backup.FileBackupAction))

        act(ConcreteFilesys())

        err = self.stderr.getvalue()
        expected = ("VERIFICATION [WARNING] " +
                    "no such file: DirBackupAction: Non-Existent source " +
                    '"%s"\n' % dirname)
        assert_substr(err, expected)
