#!/usr/bin/python

import os
import sys
import mock
from nose.tools import istest

from salve.util.context import ExecutionContext, FileContext

from salve.execute import action
from salve.execute import modify
from salve.util import ugo

from tests.utils import scratch

_testfile_dir = os.path.join(os.path.dirname(__file__), 'files')


def get_full_path(filename):
    return os.path.join(_testfile_dir, filename)


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
        File Chown Action Verify as Non-Root
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
        with mock.patch('salve.util.ugo.is_root', lambda: False), \
             mock.patch('os.stat', lambda x: mock_stat_result):
            code = act.verify_can_exec()
            assert code == act.verification_codes.NOT_ROOT, str(code)

    @istest
    def filechown_execute_nonroot(self):
        """
        File Chown Action Execute as Non-Root
        """
        self.write_file('a', '')
        a_name = self.get_fullname('a')

        act = modify.FileChownAction(a_name, 'user1', 'nogroup',
                self.file_context)

        log = {'lchown': None}

        def mock_lchown(f, uid, gid):
            log['lchown'] = (f, uid, gid)

        mock_stat_result = mock.Mock()
        # ensure a uid/gid mismatch
        mock_stat_result.st_uid = ugo.name_to_uid('user1') + 1
        mock_stat_result.st_gid = ugo.name_to_gid('nogroup') + 1

        with mock.patch('os.lchown', mock_lchown), \
             mock.patch('os.stat', lambda x: mock_stat_result), \
             mock.patch('salve.util.ugo.is_root', lambda: False):
            act()

        assert log['lchown'] is None

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

        with mock.patch('salve.util.ugo.is_owner', lambda x: False):
            code = act.verify_can_exec()
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

        with mock.patch('os.stat', lambda x: mock_stat_result), \
             mock.patch('salve.util.ugo.is_root', lambda: False):
            code = act.verify_can_exec()
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

        with mock.patch('salve.util.ugo.is_root', lambda: True):
            code = act.verify_can_exec()
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

        with mock.patch('salve.util.ugo.is_root', lambda: False), \
             mock.patch('salve.util.ugo.is_owner', lambda x: False):
            code = act.verify_can_exec()
            assert code == act.verification_codes.UNOWNED_TARGET, str(code)

    @istest
    def filechmod_execute_nonowner(self):
        """
        File Chmod Action Execute as Non-Owner
        """
        log = {'chmod': None}

        def mock_chmod(f, mode):
            log['chmod'] = (f, mode)

        # exec context transitions are silent, only higher level context
        # transitions are noisy
        self.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        act = modify.FileChmodAction('a', '600', self.file_context)

        with mock.patch('salve.execute.modify.FileChmodAction.verify_can_exec',
                lambda x: x.verification_codes.UNOWNED_TARGET):
            act()

        assert log['chmod'] is None
        assert (self.stderr.getvalue() ==
            ('[WARN] [VERIFICATION]: ' +
             'FileChmod: Unowned target file "a"\n')), self.stderr.getvalue()

    @istest
    def dirchown_execute_nonroot(self):
        """
        Directory Chown Action Execute as Non-Root
        """
        lchown_args = []

        def mock_lchown(f_or_d, uid, gid):
            lchown_args.append((f_or_d, uid, gid))

        # exec context transitions are silent, only higher level context
        # transitions are noisy
        self.exec_context.transition(ExecutionContext.phases.EXECUTION)

        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context,
                recursive=True)

        with mock.patch('salve.execute.modify.DirChownAction.verify_can_exec',
                lambda x: modify.DirChownAction.verification_codes.NOT_ROOT), \
             mock.patch('os.lchown', mock_lchown):
            act()

        assert len(lchown_args) == 0
        assert (self.stderr.getvalue() == ('[WARN] [EXECUTION]: ' +
            'DirChown: Cannot Chown as Non-Root User\n')), \
            self.stderr.getvalue()

    @istest
    def dirchmod_execute_nonowner(self):
        """
        Directory Chmod Action Execute as Non-Owner
        """
        chmod_args = []

        def mock_chmod(f_or_d, mode):
            chmod_args.append((f_or_d, mode))

        # exec context transitions are silent, only higher level context
        # transitions are noisy
        self.exec_context.transition(ExecutionContext.phases.EXECUTION)

        act = modify.DirChmodAction('a', '755', self.file_context,
                recursive=True)
        with mock.patch('os.walk', mock_os_walk), \
             mock.patch('salve.execute.modify.DirChmodAction.verify_can_exec',
                        lambda self: self.verification_codes.UNOWNED_TARGET), \
             mock.patch('os.chmod', mock_chmod):
            act()

        assert len(chmod_args) == 0
        assert (self.stderr.getvalue() == ('[WARN] [EXECUTION]: ' +
             'DirChmod: Unowned target dir "a"\n')), self.stderr.getvalue()

    @istest
    def dirchown_execute_nonrecursive_nonroot(self):
        """
        Directory Chown Action Execute Non-Recursive as Non-Root
        """
        lchown_args = []

        def mock_lchown(f_or_d, uid, gid):
            lchown_args.append((f_or_d, uid, gid))

        # exec context transitions are silent, only higher level context
        # transitions are noisy
        self.exec_context.transition(ExecutionContext.phases.EXECUTION)

        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context)
        with mock.patch('salve.execute.modify.DirChownAction.verify_can_exec',
                        lambda self: self.verification_codes.NOT_ROOT), \
             mock.patch('os.walk', mock_os_walk), \
             mock.patch('os.lchown', mock_lchown):
            act()

        assert len(lchown_args) == 0
        assert (self.stderr.getvalue() == ('[WARN] [EXECUTION]: ' +
            'DirChown: Cannot Chown as Non-Root User\n')), \
            self.stderr.getvalue()

    @istest
    def dirchmod_execute_nonrecursive_nonroot_nonowner(self):
        """
        Directory Chmod Action Execute Non-Recursive as Non-Root, Non-Owner
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
        with mock.patch('salve.execute.modify.DirChmodAction.verify_can_exec',
                lambda x: unowned_target_code), \
             mock.patch('os.walk', mock_os_walk), \
             mock.patch('os.chmod', mock_chmod):
            act()

        assert len(chmod_args) == 0
        assert (self.stderr.getvalue() == ('[WARN] [EXECUTION]: ' +
             'DirChmod: Unowned target dir "a"\n')), self.stderr.getvalue()

    @istest
    def filechown_to_str(self):
        """
        File Chown Action String Conversion
        """
        act = modify.FileChownAction('a', 'user1', 'nogroup',
                self.file_context)

        assert str(act) == ('FileChownAction(target=a,user=user1,' +
                            'group=nogroup,context=' +
                            repr(self.file_context) + ')')

    @istest
    def filechmod_to_str(self):
        """
        File Chmod Action String Conversion
        """
        act = modify.FileChmodAction('a', '600', self.file_context)

        assert str(act) == ('FileChmodAction(target=a,mode=600,' +
                            'context=' + repr(self.file_context) + ')')

    @istest
    def dirchown_to_str(self):
        """
        Directory Chown Action String Conversion
        """
        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context)

        assert str(act) == ('DirChownAction(target=a,user=user1,' +
                            'group=nogroup,recursive=False,' +
                            'context=' + repr(self.file_context) + ')')

    @istest
    def dirchmod_to_str(self):
        """
        Directory Chmod Action String Conversion
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

        with mock.patch('os.path.exists', lambda x: True), \
             mock.patch('salve.util.ugo.is_root', lambda: True):
            assert act.verify_can_exec() == act.verification_codes.OK

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

        with mock.patch('os.stat', lambda x: mock_stat_result), \
             mock.patch('salve.util.ugo.name_to_uid', lambda x: 0), \
             mock.patch('salve.util.ugo.name_to_gid', lambda x: 0), \
             mock.patch('salve.util.ugo.is_root', lambda: True):
            assert act.verify_can_exec() == act.verification_codes.OK

    @istest
    def dirchown_verify(self):
        """
        Unit: Dir Chown Action Verify
        """
        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context)

        mock_stat_result = mock.Mock()
        mock_stat_result.st_gid = 1
        mock_stat_result.st_uid = 1

        with mock.patch('os.stat', lambda x: mock_stat_result), \
             mock.patch('os.access', lambda x, y: True), \
             mock.patch('salve.util.ugo.name_to_uid', lambda x: 0), \
             mock.patch('salve.util.ugo.name_to_gid', lambda x: 0), \
             mock.patch('salve.util.ugo.is_root', lambda: True):
            assert act.verify_can_exec() == act.verification_codes.OK

    @istest
    def filechown_execute(self):
        """
        File Chown Action Execute
        """
        act = modify.FileChownAction('a', 'user1', 'nogroup',
                self.file_context)

        log = {'lchown': None}

        def mock_lchown(f, uid, gid):
            log['lchown'] = (f, uid, gid)

        with mock.patch('os.lchown', mock_lchown), \
             mock.patch('os.access', lambda x, y: True), \
             mock.patch('salve.util.ugo.name_to_uid', lambda x: 1), \
             mock.patch('salve.util.ugo.name_to_gid', lambda x: 2), \
             mock.patch('salve.util.ugo.is_root', lambda: True), \
             mock.patch('salve.execute.modify.FileChownAction.verify_can_exec',
                    lambda self: modify.FileChownAction.verification_codes.OK):
            act()

        assert log['lchown'] == ('a', 1, 2)

    @istest
    def filechmod_execute(self):
        """
        File Chmod Action Execute
        """
        act = modify.FileChmodAction('a', '600', self.file_context)

        log = {'chmod': None}

        def mock_chmod(f, mode):
            log['chmod'] = (f, mode)
        mock_stat_result = mock.Mock()
        mock_stat_result.st_uid = os.getuid()
        with mock.patch('os.chmod', mock_chmod), \
             mock.patch('os.access', lambda x, y: True), \
             mock.patch('os.stat', lambda x: mock_stat_result):
            act()
        assert log['chmod'] == ('a', int('600', 8))

    @istest
    def dirchown_execute(self):
        """
        Directory Chown Action Execute
        """
        lchown_args = []

        def mock_lchown(f_or_d, uid, gid):
            lchown_args.append((f_or_d, uid, gid))

        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context,
                recursive=True)
        with mock.patch('os.walk', mock_os_walk), \
             mock.patch('salve.util.ugo.name_to_uid', lambda x: 1), \
             mock.patch('salve.util.ugo.name_to_gid', lambda x: 2), \
             mock.patch('salve.execute.modify.DirChownAction.verify_can_exec',
                    lambda x: modify.DirChownAction.verification_codes.OK), \
             mock.patch('salve.execute.modify.FileChownAction.verify_can_exec',
                    lambda x: modify.FileChownAction.verification_codes.OK), \
             mock.patch('os.lchown', mock_lchown):
            act()

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
        Directory Chmod Action Recursive Execute
        """
        chmod_args = []

        def mock_chmod(f_or_d, mode):
            chmod_args.append((f_or_d, mode))

        mock_stat_result = mock.Mock()
        mock_stat_result.st_uid = os.getuid()

        act = modify.DirChmodAction('a', '755', self.file_context,
                recursive=True)
        with mock.patch('os.walk', mock_os_walk), \
             mock.patch('salve.execute.modify.DirChmodAction.verify_can_exec',
                    lambda x: modify.DirChmodAction.verification_codes.OK), \
             mock.patch('salve.execute.modify.FileChmodAction.verify_can_exec',
                    lambda x: modify.FileChmodAction.verification_codes.OK), \
             mock.patch('os.chmod', mock_chmod):
            act()

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
        Directory Chown Action Execute Non-Recursive
        """
        lchown_args = []

        def mock_lchown(f_or_d, uid, gid):
            lchown_args.append((f_or_d, uid, gid))

        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context)
        with mock.patch('os.walk', mock_os_walk), \
             mock.patch('salve.util.ugo.name_to_uid', lambda x: 1), \
             mock.patch('salve.util.ugo.name_to_gid', lambda x: 2), \
             mock.patch('salve.execute.modify.DirChownAction.verify_can_exec',
                    lambda x: modify.DirChownAction.verification_codes.OK), \
             mock.patch('os.lchown', mock_lchown):
            act()

        assert len(lchown_args) == 1
        assert ('a', 1, 2) in lchown_args

    @istest
    def dirchmod_execute_nonrecursive_owner(self):
        """
        Directory Chmod Action Execute Non-Recursive
        """
        chmod_args = []

        def mock_chmod(f_or_d, mode):
            chmod_args.append((f_or_d, mode))

        mock_stat_result = mock.Mock()
        mock_stat_result.st_uid = os.getuid()

        act = modify.DirChmodAction('a', '755', self.file_context)
        with mock.patch('salve.execute.modify.DirChmodAction.verify_can_exec',
                    lambda x: modify.DirChmodAction.verification_codes.OK), \
             mock.patch('os.chmod', mock_chmod):
            act()

        assert len(chmod_args) == 1
        mode = int('755', 8)
        assert ('a', mode) in chmod_args
