import os
import logging

import mock
from nose.tools import istest, eq_, ok_
from nose_parameterized import parameterized
from tests.framework import scratch, assert_substr, first_param_docfunc

from salve import ugo
from salve.context import ExecutionContext, FileContext
from salve.action import modify
from salve.filesys import ConcreteFilesys


def mock_os_walk(dir):
    l = [('a', ['b', 'c'], ['1']),
         ('a/b', [], []),
         ('a/c', ['x'], ['2', '3']),
         ('a/c/x', [], ['4'])
         ]
    for (d, sd, f) in l:
        yield (d, sd, f)


def mock_uid_and_gid(uid, gid):
    def wrapper(f):
        return mock.patch('salve.ugo.name_to_uid', lambda x: uid)(
            mock.patch('salve.ugo.name_to_gid', lambda x: gid)(
                f
            )
        )
    return wrapper


def ensure_uid_and_gid_mismatch(mock_stat):
    mock_stat.return_value.st_uid = ugo.name_to_uid('user1') + 1
    mock_stat.return_value.st_gid = ugo.name_to_gid('nogroup') + 1


def arglist_from_mock(mock_func):
    return [args[0] for args in mock_func.call_args_list]


stringification_params = [
    ('Unit: FileChownAction String Conversion', modify.FileChownAction),
    ('Unit: FileChmodAction String Conversion', modify.FileChmodAction),
    ('Unit: DirChownAction String Conversion', modify.DirChownAction),
    ('Unit: DirChmodAction String Conversion', modify.DirChmodAction),
]


class TestWithScratchdir(scratch.ScratchContainer):
    def __init__(self):
        scratch.ScratchContainer.__init__(self)
        self.walk_patch = mock.patch('os.walk', mock_os_walk)
        self.file_context = FileContext('no such file')

    def setUp(self):
        scratch.ScratchContainer.setUp(self)
        self.walk_patch.start()
        ExecutionContext()['log_level'] = logging.DEBUG

    def tearDown(self):
        scratch.ScratchContainer.tearDown(self)
        self.walk_patch.stop()

    @istest
    @mock.patch('salve.ugo.is_root', lambda: False)
    @mock.patch('salve.filesys.ConcreteFilesys.stat')
    def filechown_verify_nonroot(self, mock_stat):
        """
        Unit: File Chown Action Verify as Non-Root
        """
        self.write_file('a', '')
        a_name = self.get_fullname('a')

        act = modify.FileChownAction(a_name, 'user1', 'nogroup',
                                     self.file_context)
        ensure_uid_and_gid_mismatch(mock_stat)

        ok_(not act.verify_can_exec(ConcreteFilesys()))

    @istest
    @mock.patch('salve.filesys.ConcreteFilesys.chown')
    @mock.patch('salve.action.modify.FileChownAction.verify_can_exec')
    def filechown_execute_nonroot(self, mock_verify, mock_chown):
        """
        Unit: File Chown Action Execute as Non-Root
        """
        self.write_file('a', '')
        a_name = self.get_fullname('a')

        act = modify.FileChownAction(a_name, 'user1', 'nogroup',
                                     self.file_context)
        mock_verify.return_value = False

        act(ConcreteFilesys())

        assert not mock_chown.called

    @istest
    @mock.patch('salve.ugo.is_owner', lambda x: False)
    def filechmod_verify_nonowner(self):
        """
        Unit: File Chmod Action Verify as Non-Owner
        """
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION,
                                      quiet=True)

        self.write_file('a', '')
        a_name = self.get_fullname('a')

        act = modify.FileChmodAction(a_name, '600', self.file_context)

        ok_(not act.verify_can_exec(ConcreteFilesys()))

    @istest
    @mock.patch('salve.ugo.is_root', lambda: False)
    @mock.patch('salve.filesys.ConcreteFilesys.stat')
    def dirchown_verify_nonroot(self, mock_stat):
        """
        Unit: Dir Chown Action Verify as Non-Root
        """
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION,
                                      quiet=True)
        self.make_dir('a')
        a_name = self.get_fullname('a')

        ensure_uid_and_gid_mismatch(mock_stat)

        act = modify.DirChownAction(a_name, 'user1', 'nogroup',
                                    self.file_context)

        ok_(not act.verify_can_exec(ConcreteFilesys()))

    @istest
    @mock.patch('salve.ugo.is_root', lambda: True)
    def dirchmod_verify_root(self):
        """
        Unit: Dir Chmod Action Verify as Root
        """
        self.make_dir('a')
        a_name = self.get_fullname('a')

        # do the transition silently (suppresses debug output)
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION,
                                      quiet=True)

        act = modify.DirChmodAction(a_name, '0600', self.file_context)

        ok_(act.verify_can_exec(ConcreteFilesys()))

    @istest
    @mock.patch('salve.ugo.is_root', lambda: False)
    @mock.patch('salve.ugo.is_owner', lambda x: False)
    def dirchmod_verify_nonowner(self):
        """
        Unit: Dir Chmod Action Verify as Non-Owner
        """
        self.make_dir('a')
        a_name = self.get_fullname('a')

        # do the transition silently (suppresses debug output)
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION,
                                      quiet=True)

        act = modify.DirChmodAction(a_name, '0600', self.file_context)

        ok_(not act.verify_can_exec(ConcreteFilesys()))

    @istest
    @mock.patch('salve.action.modify.FileChmodAction.get_verification_code')
    def filechmod_execute_nonowner(self, mock_getcode):
        """
        Unit: File Chmod Action Execute as Non-Owner
        """
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION,
                                      quiet=True)

        act = modify.FileChmodAction('a', '600', self.file_context)
        mock_getcode.return_value = act.verification_codes.UNOWNED_TARGET

        act(ConcreteFilesys())

        err = self.stderr.getvalue()
        expected = 'VERIFICATION [WARNING] FileChmodAction: Unowned target "a"'
        assert_substr(err, expected)

    @istest
    @mock.patch('os.lchown')
    @mock.patch('salve.action.modify.DirChownAction.get_verification_code')
    def dirchown_execute_nonroot(self, mock_getcode, mock_lchown):
        """
        Unit: Dir Chown Action Execute as Non-Root
        """
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION,
                                      quiet=True)

        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context,
                                    recursive=True)
        mock_getcode.return_value = act.verification_codes.NOT_ROOT

        act(ConcreteFilesys())

        assert not mock_lchown.called
        err = self.stderr.getvalue()
        expected = ('EXECUTION [WARNING] DirChownAction:'
                    ' Cannot Chown as Non-Root User')
        assert_substr(err, expected)

    @istest
    @mock.patch('os.chmod')
    @mock.patch('salve.action.modify.DirChmodAction.get_verification_code')
    def dirchmod_execute_nonowner(self, mock_getcode, mock_chmod):
        """
        Unit: Dir Chmod Action Execute as Non-Owner
        """
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION,
                                      quiet=True)

        act = modify.DirChmodAction('a', '755', self.file_context,
                                    recursive=True)
        mock_getcode.return_value = act.verification_codes.UNOWNED_TARGET
        act(ConcreteFilesys())

        assert not mock_chmod.called
        err = self.stderr.getvalue()
        expected = 'EXECUTION [WARNING] DirChmodAction: Unowned target "a"'
        assert_substr(err, expected)

    @istest
    @mock.patch('os.lchown')
    @mock.patch('salve.action.modify.DirChownAction.get_verification_code')
    def dirchown_execute_nonrecursive_nonroot(self, mock_getcode, mock_lchown):
        """
        Unit: Dir Chown Action Execute Non-Recursive as Non-Root
        """
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION,
                                      quiet=True)

        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context)
        mock_getcode.return_value = act.verification_codes.NOT_ROOT
        act(ConcreteFilesys())

        assert not mock_lchown.called
        err = self.stderr.getvalue()
        expected = ('EXECUTION [WARNING] DirChownAction:'
                    ' Cannot Chown as Non-Root User')
        assert_substr(err, expected)

    @istest
    @mock.patch('os.chmod')
    @mock.patch('salve.action.modify.DirChmodAction.get_verification_code')
    def dirchmod_execute_nonrecursive_nonroot_nonowner(
            self, mock_getcode, mock_chmod):
        """
        Unit: Dir Chmod Action Execute Non-Recursive as Non-Root, Non-Owner
        """
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION,
                                      quiet=True)

        act = modify.DirChmodAction('a', '755', self.file_context)
        mock_getcode.return_value = act.verification_codes.UNOWNED_TARGET

        act(ConcreteFilesys())

        assert not mock_chmod.called
        err = self.stderr.getvalue()
        expected = 'EXECUTION [WARNING] DirChmodAction: Unowned target "a"'
        assert_substr(err, expected)

    @istest
    @mock.patch('salve.filesys.ConcreteFilesys.exists', lambda fs, x: True)
    @mock.patch('salve.ugo.is_root', lambda: True)
    def filechmod_verify_root(self):
        """
        Unit: File Chmod Action Verify (as Root)
        """
        act = modify.FileChmodAction('a', '0000', self.file_context)

        ok_(act.verify_can_exec(ConcreteFilesys()))

    @istest
    @mock.patch('salve.filesys.ConcreteFilesys.exists', lambda fs, x: True)
    @mock.patch('salve.ugo.is_root', lambda: True)
    @mock.patch('salve.filesys.ConcreteFilesys.stat')
    def filechown_verify(self, mock_stat):
        """
        Unit: File Chown Action Verify
        """
        act = modify.FileChownAction('a', 'user1', 'nogroup',
                                     self.file_context)
        ensure_uid_and_gid_mismatch(mock_stat)

        ok_(act.verify_can_exec(ConcreteFilesys()))

    @istest
    @mock.patch('salve.ugo.is_root', lambda: True)
    @mock.patch('salve.filesys.ConcreteFilesys.exists')
    @mock.patch('salve.filesys.ConcreteFilesys.access')
    @mock.patch('salve.filesys.ConcreteFilesys.stat')
    def dirchown_verify(self, mock_stat, mock_access, mock_exists):
        """
        Unit: Dir Chown Action Verify
        """
        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context)

        ensure_uid_and_gid_mismatch(mock_stat)
        mock_access.return_value = True
        mock_exists.return_value = True

        ok_(act.verify_can_exec(ConcreteFilesys()))

    @istest
    @mock_uid_and_gid(1, 2)
    @mock.patch('salve.ugo.is_root', lambda: True)
    @mock.patch('os.access', lambda x, y: True)
    @mock.patch('os.lchown')
    @mock.patch('salve.action.modify.FileChownAction.verify_can_exec')
    def filechown_execute(self, mock_verify, mock_lchown):
        """
        Unit: File Chown Action Execute
        """
        act = modify.FileChownAction('a', 'user1', 'nogroup',
                                     self.file_context)
        mock_verify.return_value = True

        act(ConcreteFilesys())

        mock_lchown.assert_called_once_with('a', 1, 2)

    @istest
    @mock.patch('salve.filesys.ConcreteFilesys.access', lambda fs, x, y: True)
    @mock.patch('salve.filesys.ConcreteFilesys.exists', lambda fs, x: True)
    @mock.patch('salve.ugo.is_owner', lambda x: True)
    @mock.patch('salve.filesys.ConcreteFilesys.chmod')
    @mock.patch('salve.filesys.ConcreteFilesys.stat')
    def filechmod_execute(self, mock_stat, mock_chmod):
        """
        Unit: File Chmod Action Execute
        """
        act = modify.FileChmodAction('a', '600', self.file_context)

        mock_stat.return_value.st_uid = os.getuid()

        act(ConcreteFilesys())

        mock_chmod.assert_called_once_with('a', int('600', 8))

    @istest
    @mock_uid_and_gid(1, 2)
    @mock.patch('os.lchown')
    @mock.patch('salve.action.modify.DirChownAction.verify_can_exec')
    @mock.patch('salve.action.modify.FileChownAction.verify_can_exec')
    def dirchown_execute(self, file_verify, dir_verify, mock_lchown):
        """
        Unit: Directory Chown Action Execute
        """
        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context,
                                    recursive=True)

        dir_verify.return_value = True
        file_verify.return_value = True

        act(ConcreteFilesys())

        lchown_args = arglist_from_mock(mock_lchown)
        eq_(len(lchown_args), 8)
        for name in ['a', 'a/b', 'a/c', 'a/1', 'a/c/2', 'a/c/3', 'a/c/x',
                     'a/c/x/4']:
            assert (name, 1, 2) in lchown_args

    @istest
    @mock.patch('os.chmod')
    @mock.patch('salve.action.modify.DirChmodAction.verify_can_exec')
    @mock.patch('salve.action.modify.FileChmodAction.verify_can_exec')
    def dirchmod_recursive_execute(self, file_verify, dir_verify, mock_chmod):
        """
        Unit: Directory Chmod Action Recursive Execute
        """
        act = modify.DirChmodAction('a', '755', self.file_context,
                                    recursive=True)

        dir_verify.return_code = True
        file_verify.return_code = True

        act(ConcreteFilesys())

        chmod_args = arglist_from_mock(mock_chmod)
        eq_(len(chmod_args), 8)
        mode = int('755', 8)
        for name in ['a', 'a/b', 'a/c', 'a/1', 'a/c/2', 'a/c/3', 'a/c/x',
                     'a/c/x/4']:
            assert (name, mode) in chmod_args

    @istest
    @mock_uid_and_gid(1, 2)
    @mock.patch('os.lchown')
    @mock.patch('salve.action.modify.DirChownAction.verify_can_exec')
    def dirchown_execute_nonrecursive(self, mock_verify, mock_lchown):
        """
        Unit: Directory Chown Action Execute Non-Recursive
        """
        act = modify.DirChownAction('a', 'user1', 'nogroup', self.file_context)
        mock_verify.return_value = True

        act(ConcreteFilesys())

        lchown_args = arglist_from_mock(mock_lchown)
        eq_(lchown_args, [('a', 1, 2)])

    @istest
    @mock.patch('os.chmod')
    @mock.patch('salve.action.modify.DirChmodAction.verify_can_exec')
    def dirchmod_execute_nonrecursive_owner(self, mock_verify, mock_chmod):
        """
        Unit: Directory Chmod Action Execute Non-Recursive
        """
        act = modify.DirChmodAction('a', '755', self.file_context)
        mock_verify.return_value = True
        act(ConcreteFilesys())

        chmod_args = arglist_from_mock(mock_chmod)
        eq_(chmod_args, [('a', int('755', 8))])

    @parameterized.expand(stringification_params,
                          testcase_func_doc=first_param_docfunc)
    @istest
    def modify_action_stringification(self, description, klass):
        args = [('target', 'a')]
        if 'Chmod' in klass.__name__:
            args.append(('mode', '600'))
            act = klass('a', '600', self.file_context)
        elif 'Chown' in klass.__name__:
            args.append(('user', 'user1'))
            args.append(('group', 'nogroup'))
            act = klass('a', 'user1', 'nogroup', self.file_context)
        else:
            assert False

        if 'Dir' in klass.__name__:
            args.append(('recursive', False))

        eq_(str(act), '{0}({1},context={2!r})'.format(
            klass.__name__,
            ','.join(['{0}={1}'.format(k, v) for (k, v) in args]),
            self.file_context))
