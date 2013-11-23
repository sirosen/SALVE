#!/usr/bin/python

import os
from nose.tools import istest
from mock import patch

from tests.utils.exceptions import ensure_except

import src.execute.backup as backup

_testfile_dir = os.path.join(os.path.dirname(__file__),'files')
def get_full_path(filename):
    return os.path.join(_testfile_dir,filename)

@istest
def backupaction_is_abstract():
    ensure_except(TypeError,backup.BackupAction)

@istest
def file_dst_dir():
    filename = get_full_path('file1.txt')
    act = backup.FileBackupAction(filename,'/etc/salve/backup')
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
    act = backup.FileBackupAction(filename,'/etc/salve/backup')

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
    act = backup.FileBackupAction(filename,'/etc/salve/backup')

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
                              '9bfabef5ffd7f5df84171393643e7ceeba916'+\
                              'e64876ace612ca8d20ad0ffd69e0ecd284ca7'+\
                              '899f4bab6805c06f881296d20f619e714befb'+\
                              '255e23fdf09ef0eed'))
