#!/usr/bin/python

import os
import mock
from nose.tools import istest

from salve import action
from salve.action import backup
from salve.filesys import ConcreteFilesys
from salve.context import ExecutionContext, FileContext

from tests.util import ensure_except, scratch, full_path
from tests.unit.action import dummy_file_context


class TestWithScratchdir(scratch.ScratchContainer):
    def setUp(self):
        scratch.ScratchContainer.setUp(self)
        ExecutionContext().set('run_log', self.stderr)
        ExecutionContext().set('backup_dir', '/etc/salve/backup')
        ExecutionContext().set('backup_log', '/etc/salve/backup.log')

    @istest
    def file_target_name(self):
        """
        Unit: File Backup Action Destination File
        Verifies that a file's abspath followed by its SHA512 hash is its
        destination file when backed up.
        """
        self.write_file('file1.txt', 'Hashing target.\n')
        filename = self.get_fullname('file1.txt')

        # a hashtable to track inputs into functions &c
        func_log = {'cp': None}

        def mock_cp(fcp_act, filesys):
            func_log['cp'] = (fcp_act.src, fcp_act.dst)

        mock_mkdir = mock.Mock()

        act = backup.FileBackupAction(filename,
                                      dummy_file_context)

        cp_exec_name = 'salve.action.copy.FileCopyAction.execute'
        backup_verify_name = \
            'salve.action.backup.FileBackupAction.verify_can_exec'
        backup_writelog_name = \
            'salve.action.backup.FileBackupAction.write_log'
        with mock.patch(cp_exec_name, mock_cp):
            with mock.patch(backup_verify_name, lambda self, fs:
                            self.verification_codes.OK):
                with mock.patch(backup_writelog_name, lambda self: None):
                    with mock.patch('salve.filesys.ConcreteFilesys.mkdir',
                                    mock_mkdir):
                        act(ConcreteFilesys())

        mock_mkdir.assert_called_once_with('/etc/salve/backup/files')

        assert os.path.basename(act.dst) == ('9bfabef5ffd7f5df84171393643' +
                                             'e7ceeba916e64876ace612ca8d2' +
                                             '0ad0ffd69e0ecd284ca7899f4ba' +
                                             'b6805c06f881296d20f619e714b' +
                                             'efb255e23fdf09ef0eed'), act.dst
        assert func_log['cp'] == (filename, act.dst)

    @istest
    def file_symlink_target_name(self):
        """
        Unit: File Backup Action Symlink Destination File
        Verifies that a symlink's abspath followed by its SHA256 hash is its
        destination file when backed up.
        """
        linkname = self.get_fullname('file_link1')
        os.symlink('file1.txt', linkname)

        # a hashtable to track inputs into functions &c
        func_log = {'cp': None}

        def mock_cp(fcp_act, filesys):
            func_log['cp'] = (fcp_act.src, fcp_act.dst)

        mock_mkdir = mock.Mock()

        act = backup.FileBackupAction(linkname,
                                      dummy_file_context)

        cp_exec_name = 'salve.action.copy.FileCopyAction.execute'
        backup_writelog_name = \
            'salve.action.backup.FileBackupAction.write_log'
        backup_verify_name = \
            'salve.action.backup.FileBackupAction.verify_can_exec'
        with mock.patch(cp_exec_name, mock_cp):
            with mock.patch(backup_writelog_name, lambda self: None):
                with mock.patch(backup_verify_name,
                                lambda self, fs: self.verification_codes.OK):
                    with mock.patch('salve.filesys.ConcreteFilesys.mkdir',
                                    mock_mkdir):
                        act(ConcreteFilesys())

        mock_mkdir.assert_called_once_with('/etc/salve/backup/files')
        assert os.path.basename(act.dst) == ('55ae75d991c770d8f3ef07cbfde' +
                                             '124ffce9c420da5db6203afab70' +
                                             '0b27e10cf9')

        assert func_log['cp'] == (linkname, act.dst)

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
        act = backup.FileBackupAction(filename,
                                      dummy_file_context)
        assert act.dst == '/etc/salve/backup/files'

    @istest
    def file_to_str(self):
        """
        Unit: File Backup Action to String

        Checks the result of converting a file backup action to a string.
        """
        filename = full_path('file1.txt')
        act = backup.FileBackupAction(filename,
                                      dummy_file_context)
        assert str(act) == \
            ('FileBackupAction(src=' + filename + ',backup_dir=' +
             '/etc/salve/backup,backup_log=/etc/salve/backup.log' +
             ',context=' + str(dummy_file_context) + ')')

    @istest
    def file_write_log(self):
        """
        Unit: File Backup Action Write Log
        Verifies that on a successful backup action, the logfile is written
        with the date, hash, and filename.
        """
        filename = full_path('file1.txt')
        act = backup.FileBackupAction(filename,
                                      dummy_file_context)
        act.hash_val = 'abc'

        mo = mock.mock_open()
        mm = mock.MagicMock()
        with mock.patch('salve.action.backup.file.open', mo, create=True):
            with mock.patch('salve.action.backup.file.print', mm, create=True):
                with mock.patch('time.strftime', lambda s: 'NOW'):
                    act.write_log()

        mo.assert_called_once_with('/etc/salve/backup.log', 'a')
        assert mm.call_args[0][0] == ('NOW abc ' + filename)

    @istest
    def dir_expand(self):
        """
        Unit: Directory Backup Action Expand Dir
        Checks the expansion of a directory into its constituent files for
        directory backups.
        """
        dirname = full_path('dir1')
        act = backup.DirBackupAction(dirname,
                                     dummy_file_context)

        def mock_execute(self, fs):
            pass
        with mock.patch('salve.action.ActionList.execute',
                        mock_execute):
            act(ConcreteFilesys())

        # must be a valid ActionList
        assert isinstance(act, action.ActionList)
        assert hasattr(act, 'actions')
        seen_files = set()
        for subact in act.actions:
            assert isinstance(subact, backup.FileBackupAction)
            seen_files.add(subact.src)
        assert full_path('dir1/a') in seen_files
        assert full_path('dir1/b') in seen_files
        assert full_path('dir1/inner_dir1/.abc') in seen_files

    @istest
    def dir_execute(self):
        """
        Unit: Directory Backup Action Execute
        Verifies that executing a DirBackupAction runs a FileBackupAction on
        each of the files in the directory.
        """
        dirname = full_path('dir1')
        act = backup.DirBackupAction(dirname, dummy_file_context)
        # check this here so that we abort the test if this condition is
        # unsatisfied, rather than starting to actually perform actions
        for subact in act.actions:
            assert isinstance(subact, backup.FileBackupAction)
        seen_files = set()
        mock_execute = lambda self, fs: seen_files.add(self.src)

        with mock.patch('salve.action.backup.FileBackupAction.execute',
                        mock_execute):
            act(ConcreteFilesys())

        assert full_path('dir1/a') in seen_files
        assert full_path('dir1/b') in seen_files
        assert full_path('dir1/inner_dir1/.abc') in seen_files

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
            assert isinstance(subact, backup.FileBackupAction)

        assert act.verify_can_exec(ConcreteFilesys()) ==\
            backup.DirBackupAction.verification_codes.NONEXISTENT_SOURCE

    @istest
    def dir_execute_no_source(self):
        """
        Unit: Directory Backup Action Execute (No Source)
        Verifies that verification of a DirBackupAction identifies missing
        source dir during execution.
        """
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        dirname = full_path('no such dir')
        act = backup.DirBackupAction(dirname, dummy_file_context)
        # check this here so that we abort the test if this condition is
        # unsatisfied, rather than starting to actually perform actions
        for subact in act.actions:
            assert isinstance(subact, backup.FileBackupAction)

        act(ConcreteFilesys())
        assert self.stderr.getvalue() == (
            "[WARN] [VERIFICATION] " +
            "no such file: DirBackup: Non-Existent source dir " +
            '"%s"\n' % dirname), self.stderr.getvalue()
