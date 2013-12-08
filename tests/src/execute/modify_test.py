#!/usr/bin/python

import os, mock
from nose.tools import istest

from src.util.error import StreamContext

import src.execute.action as action
import src.execute.modify as modify

_testfile_dir = os.path.join(os.path.dirname(__file__),'files')
def get_full_path(filename):
    return os.path.join(_testfile_dir,filename)

dummy_context = StreamContext('no such file',-1)

@istest
def filechown_to_str():
    """
    File Chown Action String Conversion
    """
    act = modify.FileChownAction('a','user1','nogroup',dummy_context)

    assert str(act) == 'FileChownAction(target=a,user=user1,'+\
                       'group=nogroup,context='+str(dummy_context)+')'

@istest
def filechmod_to_str():
    """
    File Chmod Action String Conversion
    """
    act = modify.FileChmodAction('a','600',dummy_context)

    assert str(act) == 'FileChmodAction(target=a,mode=600,'+\
                       'context='+str(dummy_context)+')'

@istest
def dirchown_to_str():
    """
    Directory Chown Action String Conversion
    """
    act = modify.DirChownAction('a','user1','nogroup',dummy_context)

    assert str(act) == 'DirChownAction(target=a,user=user1,'+\
                       'group=nogroup,recursive=False,'+\
                       'context='+str(dummy_context)+')'

@istest
def dirchmod_to_str():
    """
    Directory Chmod Action String Conversion
    """
    act = modify.DirChmodAction('a','600',dummy_context)

    assert str(act) == 'DirChmodAction(target=a,mode=600,'+\
                       'recursive=False,context='+str(dummy_context)+')'

@istest
def filechown_execute():
    """
    File Chown Action Execute
    """
    act = modify.FileChownAction('a','user1','nogroup',dummy_context)

    log = { 'lchown' : None }
    def mock_lchown(f,uid,gid): log['lchown'] = (f,uid,gid)

    with mock.patch('os.lchown',mock_lchown):
        with mock.patch('src.util.ugo.name_to_uid',lambda x: 1):
            with mock.patch('src.util.ugo.name_to_gid',lambda x: 2):
                act.execute()

    assert log['lchown'] == ('a',1,2)

@istest
def filechmod_execute():
    """
    File Chmod Action Execute
    """
    act = modify.FileChmodAction('a','600',dummy_context)

    log = { 'chmod' : None }
    def mock_chmod(f,mode): log['chmod'] = (f,mode)
    with mock.patch('os.chmod',mock_chmod): act.execute()
    assert log['chmod'] == ('a',int('600',8))

def mock_os_walk(dir):
    l = [('a',['b','c'],['1']),
         ('a/b',[],[]),
         ('a/c',['x'],['2','3']),
         ('a/c/x',[],['4'])
        ]
    for (d,sd,f) in l:
        yield (d,sd,f)

@istest
def dirchown_execute():
    """
    Directory Chown Action Execute
    """
    lchown_args = []
    def mock_lchown(f_or_d,uid,gid):
        lchown_args.append((f_or_d,uid,gid))

    act = modify.DirChownAction('a','user1','nogroup',
                                dummy_context,recursive=True)
    with mock.patch('os.walk',mock_os_walk):
        with mock.patch('src.util.ugo.name_to_uid',lambda x: 1):
            with mock.patch('src.util.ugo.name_to_gid',lambda x: 2):
                with mock.patch('os.lchown',mock_lchown):
                    act.execute()

    assert len(lchown_args) == 8
    assert ('a',1,2) in lchown_args
    assert ('a/b',1,2) in lchown_args
    assert ('a/c',1,2) in lchown_args
    assert ('a/1',1,2) in lchown_args
    assert ('a/c/2',1,2) in lchown_args
    assert ('a/c/3',1,2) in lchown_args
    assert ('a/c/x',1,2) in lchown_args
    assert ('a/c/x/4',1,2) in lchown_args

@istest
def dirchmod_execute():
    """
    Directory Chmod Action Execute
    """
    chmod_args = []
    def mock_chmod(f_or_d,mode):
        chmod_args.append((f_or_d,mode))

    act = modify.DirChmodAction('a','755',dummy_context,recursive=True)
    with mock.patch('os.walk',mock_os_walk):
        with mock.patch('src.util.ugo.name_to_uid',lambda x: 1):
            with mock.patch('src.util.ugo.name_to_gid',lambda x: 2):
                with mock.patch('os.chmod',mock_chmod):
                    act.execute()

    assert len(chmod_args) == 8
    mode = int('755',8)
    assert ('a',mode) in chmod_args
    assert ('a/b',mode) in chmod_args
    assert ('a/c',mode) in chmod_args
    assert ('a/1',mode) in chmod_args
    assert ('a/c/2',mode) in chmod_args
    assert ('a/c/3',mode) in chmod_args
    assert ('a/c/x',mode) in chmod_args
    assert ('a/c/x/4',mode) in chmod_args

@istest
def dirchown_execute_nonrecursive():
    """
    Directory Chown Action Execute Non-Recursive
    """
    lchown_args = []
    def mock_lchown(f_or_d,uid,gid):
        lchown_args.append((f_or_d,uid,gid))

    act = modify.DirChownAction('a','user1','nogroup',dummy_context)
    with mock.patch('os.walk',mock_os_walk):
        with mock.patch('src.util.ugo.name_to_uid',lambda x: 1):
            with mock.patch('src.util.ugo.name_to_gid',lambda x: 2):
                with mock.patch('os.lchown',mock_lchown):
                    act.execute()

    assert len(lchown_args) == 1
    assert ('a',1,2) in lchown_args

@istest
def dirchmod_execute_nonrecursive():
    """
    Directory Chmod Action Execute Non-Recursive
    """
    chmod_args = []
    def mock_chmod(f_or_d,mode):
        chmod_args.append((f_or_d,mode))

    act = modify.DirChmodAction('a','755',dummy_context)
    with mock.patch('os.walk',mock_os_walk):
        with mock.patch('src.util.ugo.name_to_uid',lambda x: 1):
            with mock.patch('src.util.ugo.name_to_gid',lambda x: 2):
                with mock.patch('os.chmod',mock_chmod):
                    act.execute()

    assert len(chmod_args) == 1
    mode = int('755',8)
    assert ('a',mode) in chmod_args