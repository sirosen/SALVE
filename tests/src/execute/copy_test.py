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
    log = {
        'mock_cp': None
    }
    def mock_copyfile(src,dst):
        log['mock_cp'] = (src,dst)
    def mock_name_to_uid(username): return 1
    def mock_name_to_gid(groupname): return 2

    with mock.patch('shutil.copyfile',mock_copyfile):
        fcp = copy.FileCopyAction('a',
                                  'b/c',
                                  dummy_context)
        fcp.execute()

    assert log['mock_cp'] == ('a','b/c')
