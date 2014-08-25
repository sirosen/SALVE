#!/usr/bin/python

import os
import sys
import mock
from nose.tools import istest

from salve.context import ExecutionContext, FileContext

from salve import action, ugo
from salve.action import modify
from salve.filesys import real_fs

from tests.util import scratch


def mock_os_walk(dir):
    l = [('a', ['b', 'c'], ['1']),
         ('a/b', [], []),
         ('a/c', ['x'], ['2', '3']),
         ('a/c/x', [], ['4'])
        ]
    for (d, sd, f) in l:
        yield (d, sd, f)


class TestWithScratchdir(scratch.ScratchContainer):
    def __init__(self):
        scratch.ScratchContainer.__init__(self)
        self.exec_context.set('log_level', set(('WARN', 'ERROR')))
        self.file_context = FileContext('no such file')

    @istest
    def filechown_verify_nonroot(self):
        """
        Unit: File Chown Action Verify as Non-Root
        """
        self.write_file('a', '')
        a_name = self.get_fullname('a')

        act = modify.FileChownAction(a_name, 'user1', 'nogroup',
                self.file_context)
        mock_stat_result = mock.Mock()
        # ensure a uid/gid mismatch
        mock_stat_result.st_uid = ugo.name_to_uid('user1') + 1
        mock_stat_result.st_gid = ugo.name_to_gid('nogroup') + 1

        # have to mock to be 100% certain that we are not root
        with mock.patch('salve.ugo.is_root', lambda: False):
            with mock.patch('salve.filesys.real_fs.stat',
                    lambda x: mock_stat_result):
                code = act.verify_can_exec(real_fs)

        assert code == act.verification_codes.NOT_ROOT, str(code)

    @istest
    def filechown_execute_nonroot(self):
        """
        Unit: File Chown Action Execute as Non-Root
        """
        self.write_file('a', '')
        a_name = self.get_fullname('a')

        act = modify.FileChownAction(a_name, 'user1', 'nogroup',
                self.file_context)

        mock_chown = mock.Mock()

        mock_verify = mock.Mock()
        mock_verify.return_value = \
                modify.FileChownAction.verification_codes.NOT_ROOT

        with mock.patch('salve.action.modify.FileChownAction.verify_can_exec',
                mock_verify):
            with mock.patch('salve.filesys.real_fs.chown', mock_chown):
                act(real_fs)

        assert not mock_chown.called

    @istest
    def filechmod_verify_nonowner(self):
        """
        Unit: File Chmod Action Verify as Non-Owner
        """
        self.write_file('a', '')
        a_name = self.get_fullname('a')

        # exec context transitions are silent, only higher level context
        # transitions are noisy
        self.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        act = modify.FileChmodAction(a_name, '600', self.file_context)

        with mock.patch('salve.ugo.is_owner', lambda x: False):
            code = act.verify_can_exec(real_fs)
            assert code == act.verification_codes.UNOWNED_TARGET, str(code)

    @istest
    def dirchown_verify_nonroot(self):
        """
        Unit: Dir Chown Action Verify as Non-Root
        """
        self.make_dir('a')
        a_name = self.get_fullname('a')

        # ensure mismatch between name_to_uid/name_to_gid and
        # os.stat results
        mock_stat_result = mock.Mock()
        mock_stat_result.st_uid = ugo.name_to_uid('user1') + 1
        mock_stat_result.st_gid = ugo.name_to_uid('nogroup') + 1

        # exec context transitions are silent, only higher level context
        # transitions are noisy
        self.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        act = modify.DirChownAction(a_name, 'user1', 'nogroup',
                self.file_context)

        with mock.patch('salve.filesys.real_fs.stat',
                lambda x: mock_stat_result):
            with mock.patch('salve.ugo.is_root', lambda: False):
                code = act.verify_can_exec(real_fs)
                assert code == act.verification_codes.NOT_ROOT, str(code)

    @istest
    def dirchmod_verify_root(self):
        """
        Unit: Dir Chmod Action Verify as Root
        """
        self.make_dir('a')
        a_name = self.get_fullname('a')

        # exec context transitions are silent, only higher level context
        # transitions are noisy
        self.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        act = modify.DirChmodAction(a_name, '0600', self.file_context)

        with mock.patch('salve.ugo.is_root', lambda: True):
            code = act.verify_can_exec(real_fs)
            assert code == act.verification_codes.OK, str(code)

    @istest
    def dirchmod_verify_nonowner(self):
        """
        Unit: Dir Chmod Action Verify as Non-Owner
        """
        self.make_dir('a')
        a_name = self.get_fullname('a')

        # exec context transitions are silent, only higher level context
        # transitions are noisy
        self.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        act = modify.DirChmodAction(a_name, '0600', self.file_context)

        with mock.patch('salve.ugo.is_root', lambda: False):
            with mock.patch('salve.ugo.is_owner', lambda x: False):
                code = act.verify_can_exec(real_fs)
                assert code == act.verification_codes.UNOWNED_TARGET, str(code)

    @istest
    def filechmod_execute_nonowner(self):
        """
        Unit: File Chmod Action Execute as Non-Owner
        """
        log = {'chmod': None}

        def mock_chmod(f, mode):
            log['chmod'] = (f, mode)

        # exec context transitions are silent, only higher level context
        # transitions are noisy
        self.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        act = modify.FileChmodAction('a', '600', self.file_context)

        with mock.patch('salve.action.modify.FileChmodAction.verify_can_exec',
                lambda x, fs: x.verification_codes.UNOWNED_TARGET):
            act(real_fs)

        assert log['chmod'] is None
        assert (self.stderr.getvalue() ==
            ('[WARN] [VERIFICATION] ' +
             'FileChmod: Unowned target file "a"\n')), self.stderr.getvalue()

    @istest
    def dirchown_execute_nonroot(self):
        """
        Unit: Dir Chown Action Execute as Non-Root
        """
        lchown_args = []

        def mock_lchown(f_or_d, uid, gid):
            lchown_args.append((f_or_d, uid, gid))

        # exec context transitions are silent, only higher level context
        # transitions are noisy
        self.exec_context.transition(ExecutionContext.phases.EXECUTION)

        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context,
                recursive=True)

        with mock.patch('salve.action.modify.DirChownAction.verify_can_exec',
                lambda x, fs:
                modify.DirChownAction.verification_codes.NOT_ROOT):
            with mock.patch('os.lchown', mock_lchown):
                act(real_fs)

        assert len(lchown_args) == 0
        assert (self.stderr.getvalue() == ('[WARN] [EXECUTION] ' +
            'DirChown: Cannot Chown as Non-Root User\n')), \
            self.stderr.getvalue()

    @istest
    def dirchmod_execute_nonowner(self):
        """
        Unit: Dir Chmod Action Execute as Non-Owner
        """
        chmod_args = []

        def mock_chmod(f_or_d, mode):
            chmod_args.append((f_or_d, mode))

        # exec context transitions are silent, only higher level context
        # transitions are noisy
        self.exec_context.transition(ExecutionContext.phases.EXECUTION)

        act = modify.DirChmodAction('a', '755', self.file_context,
                recursive=True)
        with mock.patch('os.walk', mock_os_walk):
            with mock.patch(
                    'salve.action.modify.DirChmodAction.verify_can_exec',
                    lambda self, fs: self.verification_codes.UNOWNED_TARGET):
                with mock.patch('os.chmod', mock_chmod):
                    act(real_fs)

        assert len(chmod_args) == 0
        assert (self.stderr.getvalue() == ('[WARN] [EXECUTION] ' +
             'DirChmod: Unowned target dir "a"\n')), self.stderr.getvalue()

    @istest
    def dirchown_execute_nonrecursive_nonroot(self):
        """
        Unit: Dir Chown Action Execute Non-Recursive as Non-Root
        """
        lchown_args = []

        def mock_lchown(f_or_d, uid, gid):
            lchown_args.append((f_or_d, uid, gid))

        # exec context transitions are silent, only higher level context
        # transitions are noisy
        self.exec_context.transition(ExecutionContext.phases.EXECUTION)

        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context)
        with mock.patch('salve.action.modify.DirChownAction.verify_can_exec',
                        lambda self, fs: self.verification_codes.NOT_ROOT):
            with mock.patch('os.walk', mock_os_walk):
                with mock.patch('os.lchown', mock_lchown):
                    act(real_fs)

        assert len(lchown_args) == 0
        assert (self.stderr.getvalue() == ('[WARN] [EXECUTION] ' +
            'DirChown: Cannot Chown as Non-Root User\n')), \
            self.stderr.getvalue()

    @istest
    def dirchmod_execute_nonrecursive_nonroot_nonowner(self):
        """
        Unit: Dir Chmod Action Execute Non-Recursive as Non-Root, Non-Owner
        """
        chmod_args = []

        def mock_chmod(f_or_d, mode):
            chmod_args.append((f_or_d, mode))

        # exec context transitions are silent, only higher level context
        # transitions are noisy
        self.exec_context.transition(ExecutionContext.phases.EXECUTION)

        act = modify.DirChmodAction('a', '755', self.file_context)

        unowned_target_code = \
                modify.DirChmodAction.verification_codes.UNOWNED_TARGET
        with mock.patch('salve.action.modify.DirChmodAction.verify_can_exec',
                lambda x, fs: unowned_target_code):
            with mock.patch('os.walk', mock_os_walk):
                with mock.patch('os.chmod', mock_chmod):
                    act(real_fs)

        assert len(chmod_args) == 0
        assert (self.stderr.getvalue() == ('[WARN] [EXECUTION] ' +
             'DirChmod: Unowned target dir "a"\n')), self.stderr.getvalue()

    @istest
    def filechown_to_str(self):
        """
        Unit: File Chown Action String Conversion
        """
        act = modify.FileChownAction('a', 'user1', 'nogroup',
                self.file_context)

        assert str(act) == ('FileChownAction(target=a,user=user1,' +
                            'group=nogroup,context=' +
                            repr(self.file_context) + ')')

    @istest
    def filechmod_to_str(self):
        """
        Unit: File Chmod Action String Conversion
        """
        act = modify.FileChmodAction('a', '600', self.file_context)

        assert str(act) == ('FileChmodAction(target=a,mode=600,' +
                            'context=' + repr(self.file_context) + ')')

    @istest
    def dirchown_to_str(self):
        """
        Unit: Directory Chown Action String Conversion
        """
        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context)

        assert str(act) == ('DirChownAction(target=a,user=user1,' +
                            'group=nogroup,recursive=False,' +
                            'context=' + repr(self.file_context) + ')')

    @istest
    def dirchmod_to_str(self):
        """
        Unit: Directory Chmod Action String Conversion
        """
        act = modify.DirChmodAction('a', '600', self.file_context)

        assert str(act) == ('DirChmodAction(target=a,mode=600,' +
                            'recursive=False,context=' +
                            repr(self.file_context) + ')')

    @istest
    def filechmod_verify_root(self):
        """
        Unit: File Chmod Action Verify (as Root)
        """
        act = modify.FileChmodAction('a', '0000', self.file_context)

        with mock.patch('salve.filesys.real_fs.exists', lambda x: True):
            with mock.patch('salve.ugo.is_root', lambda: True):
                assert act.verify_can_exec(real_fs) == \
                        act.verification_codes.OK

    @istest
    def filechown_verify(self):
        """
        Unit: File Chown Action Verify
        """
        act = modify.FileChownAction('a', 'user1', 'nogroup',
                self.file_context)

        mock_stat_result = mock.Mock()
        mock_stat_result.st_gid = 1
        mock_stat_result.st_uid = 1

        with mock.patch('salve.filesys.real_fs.stat',
                lambda x: mock_stat_result):
            with mock.patch('salve.filesys.real_fs.exists', lambda x: True):
                with mock.patch('salve.ugo.name_to_uid', lambda x: 0):
                    with mock.patch('salve.ugo.name_to_gid', lambda x: 0):
                        with mock.patch('salve.ugo.is_root',
                                lambda: True):
                            assert act.verify_can_exec(real_fs) == \
                                    act.verification_codes.OK

    @istest
    def dirchown_verify(self):
        """
        Unit: Dir Chown Action Verify
        """
        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context)

        mock_stat_result = mock.Mock()
        mock_stat_result.st_gid = 1
        mock_stat_result.st_uid = 1

        with mock.patch('salve.filesys.real_fs.stat',
                lambda x: mock_stat_result):
            with mock.patch('salve.filesys.real_fs.access', lambda x, y: True):
                with mock.patch('salve.ugo.name_to_uid', lambda x: 0):
                    with mock.patch('salve.ugo.name_to_gid',
                            lambda x: 0):
                        with mock.patch('salve.ugo.is_root',
                                lambda: True):
                            assert act.verify_can_exec(real_fs) == \
                                    act.verification_codes.OK

    @istest
    def filechown_execute(self):
        """
        Unit: File Chown Action Execute
        """
        act = modify.FileChownAction('a', 'user1', 'nogroup',
                self.file_context)

        log = {'lchown': None}

        def mock_lchown(f, uid, gid):
            log['lchown'] = (f, uid, gid)

        chown_verify_name = \
                'salve.action.modify.FileChownAction.verify_can_exec'
        mocked_verify_code = modify.FileChownAction.verification_codes.OK
        with mock.patch('os.lchown', mock_lchown):
            with mock.patch('os.access', lambda x, y: True):
                with mock.patch('salve.ugo.name_to_uid', lambda x: 1):
                    with mock.patch('salve.ugo.name_to_gid', lambda x: 2):
                        with mock.patch('salve.ugo.is_root',
                                lambda: True):
                            with mock.patch(chown_verify_name,
                                    lambda self, fs: mocked_verify_code):
                                act(real_fs)

        assert log['lchown'] == ('a', 1, 2)

    @istest
    def filechmod_execute(self):
        """
        Unit: File Chmod Action Execute
        """
        act = modify.FileChmodAction('a', '600', self.file_context)

        mock_chmod = mock.Mock()
        mock_stat_result = mock.Mock()
        mock_stat_result.st_uid = os.getuid()

        with mock.patch('salve.filesys.real_fs.chmod', mock_chmod):
            with mock.patch('salve.filesys.real_fs.access', lambda x, y: True):
                with mock.patch('salve.filesys.real_fs.exists',
                        lambda x: True):
                    with mock.patch('salve.filesys.real_fs.stat',
                            lambda x: mock_stat_result):
                        with mock.patch('salve.ugo.is_owner',
                                lambda x: True):
                            act(real_fs)

        mock_chmod.assert_called_once_with('a', int('600', 8))

    @istest
    def dirchown_execute(self):
        """
        Unit: Directory Chown Action Execute
        """
        lchown_args = []

        def mock_lchown(f_or_d, uid, gid):
            lchown_args.append((f_or_d, uid, gid))

        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context,
                recursive=True)

        dir_verify_name = 'salve.action.modify.DirChownAction.verify_can_exec'
        file_verify_name = \
                'salve.action.modify.FileChownAction.verify_can_exec'
        with mock.patch('os.walk', mock_os_walk):
            with mock.patch('salve.ugo.name_to_uid', lambda x: 1):
                with mock.patch('salve.ugo.name_to_gid', lambda x: 2):
                    with mock.patch(dir_verify_name,
                            lambda x, fs:
                            modify.DirChownAction.verification_codes.OK):
                        with mock.patch(file_verify_name,
                                lambda x, fs:
                                modify.FileChownAction.verification_codes.OK):
                            with mock.patch('os.lchown', mock_lchown):
                                act(real_fs)

        assert len(lchown_args) == 8
        assert ('a', 1, 2) in lchown_args
        assert ('a/b', 1, 2) in lchown_args
        assert ('a/c', 1, 2) in lchown_args
        assert ('a/1', 1, 2) in lchown_args
        assert ('a/c/2', 1, 2) in lchown_args
        assert ('a/c/3', 1, 2) in lchown_args
        assert ('a/c/x', 1, 2) in lchown_args
        assert ('a/c/x/4', 1, 2) in lchown_args

    @istest
    def dirchmod_recursive_execute(self):
        """
        Unit: Directory Chmod Action Recursive Execute
        """
        chmod_args = []

        def mock_chmod(f_or_d, mode):
            chmod_args.append((f_or_d, mode))

        mock_stat_result = mock.Mock()
        mock_stat_result.st_uid = os.getuid()

        act = modify.DirChmodAction('a', '755', self.file_context,
                recursive=True)

        dir_verify_name = 'salve.action.modify.DirChmodAction.verify_can_exec'
        file_verify_name = \
                'salve.action.modify.FileChmodAction.verify_can_exec'
        with mock.patch('os.walk', mock_os_walk):
            with mock.patch(dir_verify_name,
                    lambda x, fs: modify.DirChmodAction.verification_codes.OK):
                with mock.patch(file_verify_name,
                        lambda x, fs:
                        modify.FileChmodAction.verification_codes.OK):
                    with mock.patch('os.chmod', mock_chmod):
                        act(real_fs)

        assert len(chmod_args) == 8
        mode = int('755', 8)
        assert ('a', mode) in chmod_args
        assert ('a/b', mode) in chmod_args
        assert ('a/c', mode) in chmod_args
        assert ('a/1', mode) in chmod_args
        assert ('a/c/2', mode) in chmod_args
        assert ('a/c/3', mode) in chmod_args
        assert ('a/c/x', mode) in chmod_args
        assert ('a/c/x/4', mode) in chmod_args

    @istest
    def dirchown_execute_nonrecursive(self):
        """
        Unit: Directory Chown Action Execute Non-Recursive
        """
        lchown_args = []

        def mock_lchown(f_or_d, uid, gid):
            lchown_args.append((f_or_d, uid, gid))

        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context)

        dir_verify_name = 'salve.action.modify.DirChownAction.verify_can_exec'
        with mock.patch('os.walk', mock_os_walk):
            with mock.patch('salve.ugo.name_to_uid', lambda x: 1):
                with mock.patch('salve.ugo.name_to_gid', lambda x: 2):
                    with mock.patch(dir_verify_name,
                            lambda x, fs:
                            modify.DirChownAction.verification_codes.OK):
                        with mock.patch('os.lchown', mock_lchown):
                            act(real_fs)

        assert len(lchown_args) == 1
        assert ('a', 1, 2) in lchown_args

    @istest
    def dirchmod_execute_nonrecursive_owner(self):
        """
        Unit: Directory Chmod Action Execute Non-Recursive
        """
        chmod_args = []

        def mock_chmod(f_or_d, mode):
            chmod_args.append((f_or_d, mode))

        mock_stat_result = mock.Mock()
        mock_stat_result.st_uid = os.getuid()

        act = modify.DirChmodAction('a', '755', self.file_context)
        with mock.patch('salve.action.modify.DirChmodAction.verify_can_exec',
                    lambda x, fs: modify.DirChmodAction.verification_codes.OK):
            with mock.patch('os.chmod', mock_chmod):
                act(real_fs)

        assert len(chmod_args) == 1
        mode = int('755', 8)
        assert ('a', mode) in chmod_args
