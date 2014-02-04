#!/usr/bin/python

import os
import mock
import StringIO
from nose.tools import istest

from src.util.error import StreamContext

import src.execute.action as action
import src.execute.modify as modify

import tests.utils.scratch as scratch

_testfile_dir = os.path.join(os.path.dirname(__file__),'files')
def get_full_path(filename):
    return os.path.join(_testfile_dir,filename)

dummy_context = StreamContext('no such file',-1)

class TestWithScratchdir(scratch.ScratchContainer):
    @istest
    def filechown_execute_nonroot(self):
        """
        File Chown Action Execute as Non-Root
        """
        self.write_file('a','')
        a_name = self.get_fullname('a')

        act = modify.FileChownAction(a_name,'user1','nogroup',dummy_context)

        log = { 'lchown' : None }
        def mock_lchown(f,uid,gid): log['lchown'] = (f,uid,gid)

        with mock.patch('os.lchown',mock_lchown), \
             mock.patch('src.util.ugo.is_root',lambda: False):
            act()

        assert log['lchown'] is None

@istest
def filechmod_execute_nonowner():
    """
    File Chmod Action Execute as Non-Owner
    """
    act = modify.FileChmodAction('a','600',dummy_context)

    log = { 'chmod' : None }
    def mock_chmod(f,mode): log['chmod'] = (f,mode)

    fake_stderr = StringIO.StringIO()
    with mock.patch('src.execute.modify.FileChmodAction.verify_can_exec',
                    lambda self: self.verification_codes.UNOWNED_TARGET), \
         mock.patch('sys.stderr',fake_stderr):
        act()

    assert log['chmod'] is None
    assert fake_stderr.getvalue() == \
        'no such file, line -1: FileChmodWarning: Unowned target file "a"\n'

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

    with mock.patch('os.lchown',mock_lchown), \
         mock.patch('os.access',lambda x,y: True), \
         mock.patch('src.util.ugo.name_to_uid',lambda x: 1), \
         mock.patch('src.util.ugo.name_to_gid',lambda x: 2), \
         mock.patch('src.util.ugo.is_root',lambda: True), \
         mock.patch('src.execute.modify.FileChownAction.verify_can_exec',
                    lambda self: modify.FileChownAction.verification_codes.OK):
        act()

    assert log['lchown'] == ('a',1,2)

@istest
def filechmod_execute():
    """
    File Chmod Action Execute
    """
    act = modify.FileChmodAction('a','600',dummy_context)

    log = { 'chmod' : None }
    def mock_chmod(f,mode): log['chmod'] = (f,mode)
    mock_stat_result = mock.Mock()
    mock_stat_result.st_uid = os.getuid()
    with mock.patch('os.chmod',mock_chmod), \
         mock.patch('os.access',lambda x,y: True), \
         mock.patch('os.stat',lambda x: mock_stat_result):
        act()
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
    with mock.patch('os.walk',mock_os_walk), \
         mock.patch('src.util.ugo.name_to_uid',lambda x: 1), \
         mock.patch('src.util.ugo.name_to_gid',lambda x: 2), \
         mock.patch('src.execute.modify.DirChownAction.verify_can_exec',
                    lambda x: modify.DirChownAction.verification_codes.OK), \
         mock.patch('src.execute.modify.FileChownAction.verify_can_exec',
                    lambda x: modify.FileChownAction.verification_codes.OK), \
         mock.patch('os.lchown',mock_lchown):
                    act()

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
def dirchown_execute_nonroot():
    """
    Directory Chown Action Execute as Non-Root
    """
    lchown_args = []
    def mock_lchown(f_or_d,uid,gid):
        lchown_args.append((f_or_d,uid,gid))

    fake_stderr = StringIO.StringIO()

    act = modify.DirChownAction('a','user1','nogroup',
                                dummy_context,recursive=True)

    with mock.patch('src.execute.modify.DirChownAction.verify_can_exec',
                    lambda x: modify.DirChownAction.verification_codes.NOT_ROOT), \
         mock.patch('sys.stderr', fake_stderr), \
         mock.patch('os.lchown', mock_lchown):
        act()

    assert len(lchown_args) == 0
    assert fake_stderr.getvalue() == \
        'no such file, line -1: DirChownWarning: Cannot Chown as Non-Root User\n'

@istest
def dirchmod_recursive_execute():
    """
    Directory Chmod Action Recursive Execute
    """
    chmod_args = []
    def mock_chmod(f_or_d,mode):
        chmod_args.append((f_or_d,mode))

    mock_stat_result = mock.Mock()
    mock_stat_result.st_uid = os.getuid()

    act = modify.DirChmodAction('a','755',dummy_context,recursive=True)
    with mock.patch('os.walk',mock_os_walk), \
         mock.patch('src.execute.modify.DirChmodAction.verify_can_exec',
                    lambda x: modify.DirChmodAction.verification_codes.OK), \
         mock.patch('src.execute.modify.FileChmodAction.verify_can_exec',
                    lambda x: modify.FileChmodAction.verification_codes.OK), \
         mock.patch('os.chmod',mock_chmod):
        act()

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
def dirchmod_execute_nonowner():
    """
    Directory Chmod Action Execute as Non-Owner
    """
    chmod_args = []
    def mock_chmod(f_or_d,mode):
        chmod_args.append((f_or_d,mode))
    fake_stderr = StringIO.StringIO()

    act = modify.DirChmodAction('a','755',dummy_context,recursive=True)
    with mock.patch('os.walk',mock_os_walk), \
         mock.patch('src.execute.modify.DirChmodAction.verify_can_exec',
                    lambda self: self.verification_codes.UNOWNED_TARGET), \
         mock.patch('sys.stderr',fake_stderr), \
         mock.patch('os.chmod',mock_chmod):
        act()

    assert len(chmod_args) == 0
    assert fake_stderr.getvalue() == \
        'no such file, line -1: DirChmodWarning: Unowned target dir "a"\n'

@istest
def dirchown_execute_nonrecursive():
    """
    Directory Chown Action Execute Non-Recursive
    """
    lchown_args = []
    def mock_lchown(f_or_d,uid,gid):
        lchown_args.append((f_or_d,uid,gid))

    act = modify.DirChownAction('a','user1','nogroup',dummy_context)
    with mock.patch('os.walk',mock_os_walk), \
         mock.patch('src.util.ugo.name_to_uid',lambda x: 1), \
         mock.patch('src.util.ugo.name_to_gid',lambda x: 2), \
         mock.patch('src.execute.modify.DirChownAction.verify_can_exec',
                    lambda x: modify.DirChownAction.verification_codes.OK), \
         mock.patch('os.lchown',mock_lchown):
        act()

    assert len(lchown_args) == 1
    assert ('a',1,2) in lchown_args

@istest
def dirchmod_execute_nonrecursive_owner():
    """
    Directory Chmod Action Execute Non-Recursive
    """
    chmod_args = []
    def mock_chmod(f_or_d,mode):
        chmod_args.append((f_or_d,mode))

    mock_stat_result = mock.Mock()
    mock_stat_result.st_uid = os.getuid()

    act = modify.DirChmodAction('a','755',dummy_context)
    with mock.patch('src.execute.modify.DirChmodAction.verify_can_exec',
                    lambda x: modify.DirChmodAction.verification_codes.OK), \
         mock.patch('os.chmod',mock_chmod):
        act()

    assert len(chmod_args) == 1
    mode = int('755',8)
    assert ('a',mode) in chmod_args

@istest
def dirchown_execute_nonrecursive_nonroot():
    """
    Directory Chown Action Execute Non-Recursive as Non-Root
    """
    lchown_args = []
    def mock_lchown(f_or_d,uid,gid):
        lchown_args.append((f_or_d,uid,gid))

    fake_stderr = StringIO.StringIO()

    act = modify.DirChownAction('a','user1','nogroup',dummy_context)
    with mock.patch('src.execute.modify.DirChownAction.verify_can_exec',
                    lambda self: self.verification_codes.NOT_ROOT), \
         mock.patch('os.walk',mock_os_walk), \
         mock.patch('sys.stderr',fake_stderr), \
         mock.patch('os.lchown',mock_lchown):
        act()

    assert len(lchown_args) == 0
    assert fake_stderr.getvalue() == \
        'no such file, line -1: DirChownWarning: Cannot Chown as Non-Root User\n'

@istest
def dirchmod_execute_nonrecursive_nonroot_nonowner():
    """
    Directory Chmod Action Execute Non-Recursive as Non-Root, Non-Owner
    """
    chmod_args = []
    def mock_chmod(f_or_d,mode):
        chmod_args.append((f_or_d,mode))

    fake_stderr = StringIO.StringIO()

    act = modify.DirChmodAction('a','755',dummy_context)
    with mock.patch('src.execute.modify.DirChmodAction.verify_can_exec',
                    lambda x: modify.DirChmodAction.verification_codes.UNOWNED_TARGET), \
         mock.patch('os.walk',mock_os_walk), \
         mock.patch('sys.stderr',fake_stderr), \
         mock.patch('os.chmod',mock_chmod):
        act()

    assert len(chmod_args) == 0
    assert fake_stderr.getvalue() == \
        'no such file, line -1: DirChmodWarning: Unowned target dir "a"\n'
