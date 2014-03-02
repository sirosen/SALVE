#!/usr/bin/python

import os
import mock
from nose.tools import istest

from tests.utils.exceptions import ensure_except
from src.util.context import SALVEContext, ExecutionContext, StreamContext
import tests.utils.scratch as scratch

import src.execute.action as action
import src.execute.backup as backup

_testfile_dir = os.path.join(os.path.dirname(__file__),'files')
def get_full_path(filename):
    return os.path.join(_testfile_dir,filename)

dummy_stream_context = StreamContext('no such file',-1)
dummy_exec_context = ExecutionContext()
dummy_exec_context.set('backup_dir','/etc/salve/backup')
dummy_exec_context.set('backup_log','/etc/salve/backup.log')
dummy_context = SALVEContext(stream_context=dummy_stream_context,
                             exec_context=dummy_exec_context)

class TestWithScratchdir(scratch.ScratchContainer):
    @istest
    def file_target_name(self):
        """
        File Backup Action Destination File
        Verifies that a file's abspath followed by its SHA512 hash is its
        destination file when backed up.
        """
        self.write_file('file1.txt','Hashing target.\n')
        filename = self.get_fullname('file1.txt')

        # a hashtable to track inputs into functions &c
        func_log = {'cp':None}

        def mock_cp(fcp_act):
            func_log['cp'] = (fcp_act.src,fcp_act.dst)

        def mock_exists(path):
            if path == '/etc/salve/backup' or path == '/etc/salve/backup/files':
                return True
            else:
                return False

        act = backup.FileBackupAction(filename,
                                      dummy_context)

        with mock.patch('src.execute.copy.FileCopyAction.execute',mock_cp), \
             mock.patch('src.execute.backup.FileBackupAction.verify_can_exec',
                        lambda self: self.verification_codes.OK), \
             mock.patch('src.execute.backup.FileBackupAction.write_log',
                        lambda self: None), \
             mock.patch('os.path.exists',mock_exists):
            act()

        assert os.path.basename(act.dst) == '9bfabef5ffd7f5df84171393643'+\
                                            'e7ceeba916e64876ace612ca8d2'+\
                                            '0ad0ffd69e0ecd284ca7899f4ba'+\
                                            'b6805c06f881296d20f619e714b'+\
                                            'efb255e23fdf09ef0eed', act.dst

        assert func_log['cp'] == (filename,act.dst)

    @istest
    def file_symlink_target_name(self):
        """
        File Backup Action Symlink Destination File
        Verifies that a symlink's abspath followed by its SHA256 hash is its
        destination file when backed up.
        """
        linkname = self.get_fullname('file_link1')
        os.symlink('file1.txt',linkname)

        # a hashtable to track inputs into functions &c
        func_log = {'cp':None}

        def mock_cp(fcp_act):
            func_log['cp'] = (fcp_act.src,fcp_act.dst)

        def mock_exists(path):
            if path == '/etc/salve/backup' or path == '/etc/salve/backup/files':
                return True
            else:
                return False

        act = backup.FileBackupAction(linkname,
                                      dummy_context)

        with mock.patch('src.execute.copy.FileCopyAction.execute',mock_cp), \
             mock.patch('src.execute.backup.FileBackupAction.write_log',
                        lambda self: None), \
             mock.patch('src.execute.backup.FileBackupAction.verify_can_exec',
                        lambda self: self.verification_codes.OK), \
             mock.patch('os.path.exists',mock_exists):
            act()

        assert os.path.basename(act.dst) == '55ae75d991c770d8f3ef07cbfde'+\
                                            '124ffce9c420da5db6203afab70'+\
                                            '0b27e10cf9'

        assert func_log['cp'] == (linkname,act.dst)

@istest
def backupaction_is_abstract():
    """
    Backup Action Base Class Is Abstract
    Checks that instantiating a BackupAction raises an error.
    """
    ensure_except(TypeError,backup.BackupAction)

@istest
def file_dst_dir():
    """
    File Backup Action Destination Directory
    Verifies that a file's abspath becomes its storage directory under
    the backup dir.
    """
    filename = get_full_path('file1.txt')
    act = backup.FileBackupAction(filename,
                                  dummy_context)
    assert act.dst == '/etc/salve/backup/files'

@istest
def file_to_str():
    """
    File Backup Action to String

    Checks the result of converting a file backup action to a string.
    """
    filename = get_full_path('file1.txt')
    act = backup.FileBackupAction(filename,
                                  dummy_context)
    assert str(act) == \
        'FileBackupAction(src='+filename+',backup_dir='+\
        '/etc/salve/backup,backup_log=/etc/salve/backup.log'+\
        ',context='+str(dummy_context)+')'

@istest
def file_write_log():
    """
    File Backup Action Write Log
    Verifies that on a successful backup action, the logfile is written
    with the date, hash, and filename.
    """
    filename = get_full_path('file1.txt')
    act = backup.FileBackupAction(filename,
                                  dummy_context)
    act.hash_val = 'abc'

    mo = mock.mock_open()
    mm = mock.MagicMock()
    with mock.patch('src.execute.backup.open',mo,create=True), \
         mock.patch('src.execute.backup.print',mm,create=True), \
         mock.patch('time.strftime',lambda s: 'NOW'):
        act.write_log()

    mo.assert_called_once_with('/etc/salve/backup.log','a')
    assert mm.call_args[0][0] == ('NOW abc ' + filename)

@istest
def dir_expand():
    """
    Directory Backup Action Expand Dir
    Checks the expansion of a directory into its constituent files for
    directory backups.
    """
    dirname = get_full_path('dir1')
    act = backup.DirBackupAction(dirname,
                                 dummy_context)

    def mock_execute(self): pass
    with mock.patch('src.execute.action.ActionList.execute',
                    mock_execute):
        act()

    # must be a valid ActionList
    assert isinstance(act,action.ActionList)
    assert hasattr(act,'actions')
    seen_files = set()
    for subact in act.actions:
        assert isinstance(subact,backup.FileBackupAction)
        seen_files.add(subact.src)
    assert get_full_path('dir1/a') in seen_files
    assert get_full_path('dir1/b') in seen_files
    assert get_full_path('dir1/inner_dir1/.abc') in seen_files

@istest
def dir_execute():
    """
    Directory Backup Action Execute
    Verifies that executing a DirBackupAction runs a FileBackupAction on
    each of the files in the directory.
    """
    dirname = get_full_path('dir1')
    act = backup.DirBackupAction(dirname,dummy_context)
    # check this here so that we abort the test if this condition is
    # unsatisfied, rather than starting to actually perform actions
    for subact in act.actions:
        assert isinstance(subact,backup.FileBackupAction)
    seen_files = set()
    mock_execute = lambda self: seen_files.add(self.src)

    with mock.patch('src.execute.backup.FileBackupAction.execute',
                    mock_execute):
        act()

    assert get_full_path('dir1/a') in seen_files
    assert get_full_path('dir1/b') in seen_files
    assert get_full_path('dir1/inner_dir1/.abc') in seen_files
