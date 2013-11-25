#!/usr/bin/python

import os, mock
from nose.tools import istest
from mock import patch

from tests.utils.exceptions import ensure_except
from src.util.error import StreamContext

import src.execute.action as action
import src.execute.backup as backup

_testfile_dir = os.path.join(os.path.dirname(__file__),'files')
def get_full_path(filename):
    return os.path.join(_testfile_dir,filename)

dummy_context = StreamContext('no such file',-1)

@istest
def backupaction_is_abstract():
    ensure_except(TypeError,backup.BackupAction)

@istest
def file_dst_dir():
    filename = get_full_path('file1.txt')
    act = backup.FileBackupAction(filename,'/etc/salve/backup',
                                  '/etc/salve/backup.log',dummy_context)
    assert act.dst == os.path.join('/etc/salve/backup',
                                   filename.lstrip('/'))

@istest
def file_target_name():
    # a hashtable to track inputs into functions &c
    func_log = {}
    def mock_makedirs(dirname):
        func_log['makedirs'] = dirname
    def mock_exists(filename): False
    real_islink = os.path.islink
    def mock_islink(filename):
        func_log['islink'] = real_islink(filename)
        return False
    def mock_cp(src,dst):
        func_log['cp'] = (src,dst)

    filename = get_full_path('file1.txt')
    act = backup.FileBackupAction(filename,'/etc/salve/backup',
                                  '/etc/salve/backup.log',dummy_context)

    with patch('src.execute.backup.FileBackupAction.write_log',lambda self: None):
        with patch('os.makedirs',mock_makedirs):
            with patch('os.path.exists',mock_exists):
                with patch('os.path.islink',mock_islink):
                    with patch('shutil.copyfile',mock_cp):
                        act.execute()

    assert 'makedirs' in func_log
    assert func_log['makedirs'] == act.dst
    assert 'islink' in func_log
    assert func_log['islink'] == False
    assert 'cp' in func_log
    assert func_log['cp'] == (filename,
                              os.path.join(act.dst,
                              '9bfabef5ffd7f5df84171393643e7ceeba916'+\
                              'e64876ace612ca8d20ad0ffd69e0ecd284ca7'+\
                              '899f4bab6805c06f881296d20f619e714befb'+\
                              '255e23fdf09ef0eed'))

@istest
def file_symlink_target_name():
    # a hashtable to track inputs into functions &c
    func_log = {}
    def mock_makedirs(dirname):
        func_log['makedirs'] = dirname
    def mock_exists(filename): False
    real_islink = os.path.islink
    def mock_islink(filename):
        func_log['islink'] = real_islink(filename)
        return True
    def mock_link(src,dst):
        func_log['ln'] = (src,dst)

    filename = get_full_path('file_link1')
    act = backup.FileBackupAction(filename,'/etc/salve/backup',
                                  '/etc/salve/backup.log',dummy_context)

    with patch('src.execute.backup.FileBackupAction.write_log',lambda self: None):
        with patch('os.makedirs',mock_makedirs):
            with patch('os.path.exists',mock_exists):
                with patch('os.path.islink',mock_islink):
                    with patch('os.symlink',mock_link):
                        act.execute()

    assert 'makedirs' in func_log
    assert func_log['makedirs'] == act.dst
    assert 'islink' in func_log
    assert func_log['islink'] == True
    assert 'ln' in func_log
    assert func_log['ln'] == (os.readlink(filename),
                              os.path.join(act.dst,
                              '55ae75d991c770d8f3ef07cbfde124ffce9c4'+\
                              '20da5db6203afab700b27e10cf9'))

@istest
def file_write_log():
    filename = get_full_path('file1.txt')
    act = backup.FileBackupAction(filename,'/etc/salve/backup',
                                  '/etc/salve/backup.log',dummy_context)
    act.hash_val = 'abc'

    mo = mock.mock_open()
    mm = mock.MagicMock()
    with patch('src.execute.backup.open',mo,create=True):
        with patch('src.execute.backup.print',mm,create=True):
            with patch('time.strftime',lambda s: 'NOW'):
                act.write_log()

    mo.assert_called_once_with('/etc/salve/backup.log','a')
    assert mm.call_args[0][0] == ('NOW abc ' + filename)

@istest
def dir_expand():
    dirname = get_full_path('dir1')
    act = backup.DirBackupAction(dirname,'/etc/salve/backup',
                                 '/etc/salve/backup.log',dummy_context)

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
    dirname = get_full_path('dir1')
    act = backup.DirBackupAction(dirname,'/etc/salve/backup',
                                 '/etc/salve/backup.log',dummy_context)
    # check this here so that we abort the test if this condition is
    # unsatisfied, rather than starting to actually perform actions
    for subact in act.actions:
        assert isinstance(subact,backup.FileBackupAction)
    seen_files = set()
    mock_execute = lambda self: seen_files.add(self.src)

    with patch('src.execute.backup.FileBackupAction.execute',
               mock_execute):
        act.execute()

    assert get_full_path('dir1/a') in seen_files
    assert get_full_path('dir1/b') in seen_files
    assert get_full_path('dir1/inner_dir1/.abc') in seen_files
