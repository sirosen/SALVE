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
                              'user1',
                              'group1',
                              '600',
                              dummy_context)

    mode = '{0:o}'.format(fcp.mode)
    assert str(fcp) == 'FileCopyAction(src=a,dst=b/c,user=user1,'+\
        'group=group1,mode='+mode+',context='+str(dummy_context)+')'

@istest
def filecopy_execute_no_root():
    log = {
        'mock_cp': None,
        'mock_chmod': None
    }
    def mock_copyfile(src,dst):
        log['mock_cp'] = (src,dst)
    def mock_chmod(dst,mode):
        log['mock_chmod'] = (dst,mode)

    with mock.patch('shutil.copyfile',mock_copyfile):
        with mock.patch('os.chmod',mock_chmod):
            with mock.patch('src.util.ugo.is_root',lambda: False):
                fcp = copy.FileCopyAction('a',
                                          'b/c',
                                          'user1',
                                          'group1',
                                          '600',
                                          dummy_context)
                fcp.execute()

    assert log['mock_cp'] == ('a','b/c')
    assert log['mock_chmod'] == ('b/c',int('600',8))

@istest
def filecopy_execute():
    log = {
        'mock_cp': None,
        'mock_chmod': None,
        'mock_chown': None
    }
    def mock_copyfile(src,dst):
        log['mock_cp'] = (src,dst)
    def mock_chmod(dst,mode):
        log['mock_chmod'] = (dst,mode)
    def mock_lchown(dst,uid,gid):
        log['mock_chown'] = (dst,uid,gid)
    def mock_name_to_uid(username): return 1
    def mock_name_to_gid(groupname): return 2

    with mock.patch('shutil.copyfile',mock_copyfile):
        with mock.patch('os.chmod',mock_chmod):
            with mock.patch('src.util.ugo.is_root',lambda: True):
                with mock.patch('src.util.ugo.name_to_uid',
                                mock_name_to_uid):
                    with mock.patch('src.util.ugo.name_to_gid',
                                    mock_name_to_gid):
                        fcp = copy.FileCopyAction('a',
                                                  'b/c',
                                                  'user1',
                                                  'group1',
                                                  '600',
                                                  dummy_context)
                        fcp.execute()

    assert log['mock_cp'] == ('a','b/c')
    assert log['mock_chmod'] == ('b/c',int('600',8))
    assert log['mock_chown'] == ('b/c',1,2)
