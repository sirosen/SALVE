#!/usr/bin/python

import os, mock
from nose.tools import istest

from src.util.error import StreamContext

import src.execute.action as action
import src.execute.copy as copy

_testfile_dir = os.path.join(os.path.dirname(__file__),'files')
def get_full_path(filename):
    return os.path.join(_testfile_dir,filename)

dummy_context = StreamContext('no such file',-1)

@istest
def filecopy_to_str():
    """
    File Copy Action String Conversion
    """
    fcp = copy.FileCopyAction('a',
                              'b/c',
                              dummy_context)

    assert str(fcp) == 'FileCopyAction(src=a,dst=b/c,context='+\
                       str(dummy_context)+')'

@istest
def filecopy_execute():
    """
    File Copy Action Execution
    """
    log = {
        'mock_cp': None
    }
    def mock_copyfile(src,dst):
        log['mock_cp'] = (src,dst)
    def mock_name_to_uid(username): return 1
    def mock_name_to_gid(groupname): return 2

    with mock.patch('shutil.copyfile',mock_copyfile), \
         mock.patch('os.access', lambda x,y: True):
        fcp = copy.FileCopyAction('a',
                                  'b/c',
                                  dummy_context)
        fcp()

    assert log['mock_cp'] == ('a','b/c')

@istest
def dircopy_to_str():
    """
    Directory Copy Action String Conversion
    """
    dcp = copy.DirCopyAction('a',
                             'b/c',
                             dummy_context)

    assert str(dcp) == 'DirCopyAction(src=a,dst=b/c,context='+\
                       str(dummy_context)+')'

@istest
def dircopy_execute():
    """
    Directory Copy Action Execution
    """
    log = {
        'mock_cp': None
    }
    def mock_copytree(src,dst,symlinks=None):
        log['mock_cp'] = (src,dst,symlinks)
    def mock_name_to_uid(username): return 1
    def mock_name_to_gid(groupname): return 2

    with mock.patch('shutil.copytree',mock_copytree), \
         mock.patch('os.access', lambda x,y: True):
        dcp = copy.DirCopyAction('a',
                                  'b/c',
                                  dummy_context)
        dcp()

    assert log['mock_cp'] == ('a','b/c',True)
