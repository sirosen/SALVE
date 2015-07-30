#!/usr/bin/python

import os
import mock
from nose.tools import istest

from salve.context import ExecutionContext, FileContext

from salve import action
from salve.action import copy
from salve.filesys import ConcreteFilesys
from tests.util import scratch


class TestWithScratchdir(scratch.ScratchContainer):
    def __init__(self):
        scratch.ScratchContainer.__init__(self)
        self.dummy_file_context = FileContext('no such file')

    @istest
    def filecopy_execute(self):
        """
        Unit: File Copy Action Execution
        """
        content = 'a b c d \n e f g'
        self.write_file('a', content)
        self.make_dir('b')
        a_name = self.get_fullname('a')
        b_name = self.get_fullname('b')

        fcp = copy.FileCopyAction(a_name,
                                  os.path.join(b_name, 'c'),
                                  self.dummy_file_context)
        fcp(ConcreteFilesys())

        assert content == self.read_file('b/c')

    @istest
    def canexec_unwritable_target(self):
        """
        Unit: File Copy Action Verify Unwritable Target
        Checks the results of a verification check when the target
        is an unwritable file.
        """
        content = 'abc'
        self.write_file('a', content)
        content = 'efg'
        self.write_file('b', content)
        a_name = self.get_fullname('a')
        b_name = self.get_fullname('b')

        os.chmod(b_name, 0o444)
        fcp = copy.FileCopyAction(a_name, b_name,
                                  self.dummy_file_context)

        assert fcp.verify_can_exec(ConcreteFilesys()) == \
            fcp.verification_codes.UNWRITABLE_TARGET

    @istest
    def canexec_unwritable_target_dir(self):
        """
        Unit: File Copy Action Verify Unwritable Target Directory
        Checks the results of a verification check when the target
        is in an unwritable directory.
        """
        content = 'abc'
        self.write_file('a', content)
        self.make_dir('b')
        content = 'efg'
        self.write_file('b/c', content)
        a_name = self.get_fullname('a')
        b_name = self.get_fullname('b')
        c_name = self.get_fullname('b/c')

        os.chmod(b_name, 0o000)
        fcp = copy.FileCopyAction(a_name, c_name,
                                  self.dummy_file_context)

        vcode = fcp.verify_can_exec(ConcreteFilesys())

        assert vcode == fcp.verification_codes.UNWRITABLE_TARGET

    @istest
    def canexec_unreadable_source(self):
        """
        Unit: File Copy Action Verify Unreadable Source
        Checks the results of a verification check when the source
        is an unreadable file.
        """
        content = 'abc'
        self.write_file('a', content)
        content = 'efg'
        self.write_file('b', content)
        a_name = self.get_fullname('a')
        b_name = self.get_fullname('b')

        os.chmod(a_name, 0o000)
        fcp = copy.FileCopyAction(a_name, b_name,
                                  self.dummy_file_context)

        assert fcp.verify_can_exec(ConcreteFilesys()) == \
            fcp.verification_codes.UNREADABLE_SOURCE

    @istest
    def dir_canexec_unreadable_source(self):
        """
        Unit: Dir Copy Action Verify Unreadable Source
        Checks the results of a verification check when the source
        is an unreadable dir.
        """
        self.make_dir('a')
        a_name = self.get_fullname('a')
        b_name = self.get_fullname('b')

        dcp = copy.DirCopyAction(a_name, b_name,
                                 self.dummy_file_context)

        mock_access = mock.Mock()
        mock_access.return_value = False

        with mock.patch('salve.filesys.ConcreteFilesys.access', mock_access):
            assert dcp.verify_can_exec(ConcreteFilesys()) == \
                dcp.verification_codes.UNREADABLE_SOURCE

    @istest
    def dir_canexec_unwritable_target(self):
        """
        Unit: Dir Copy Action Verify Unwritable Target
        Checks the results of a verification check when the target
        is an unwritable directory.
        """
        self.make_dir('a')
        self.make_dir('b')

        a_name = self.get_fullname('a')
        b_name = self.get_fullname('b')
        os.chmod(b_name, 0o444)

        c_name = self.get_fullname('b/c')
        dcp = copy.DirCopyAction(a_name, c_name,
                                 self.dummy_file_context)

        assert dcp.verify_can_exec(ConcreteFilesys()) == \
            dcp.verification_codes.UNWRITABLE_TARGET

    @istest
    def filecopy_to_str(self):
        """
        Unit: File Copy Action String Conversion
        """
        fcp = copy.FileCopyAction('a', 'b/c', self.dummy_file_context)

        assert str(fcp) == ('FileCopyAction(src=a,dst=b/c,context=' +
                            repr(self.dummy_file_context) + ')')

    @istest
    def dircopy_to_str(self):
        """
        Unit: Directory Copy Action String Conversion
        """
        dcp = copy.DirCopyAction('a',
                                 'b/c',
                                 self.dummy_file_context)

        assert str(dcp) == ('DirCopyAction(src=a,dst=b/c,context=' +
                            repr(self.dummy_file_context) + ')')

    @istest
    def dircopy_execute(self):
        """
        Unit: Directory Copy Action Execution
        """
        mock_copy = mock.Mock()
        mock_copy.return_value = None

        def mock_name_to_uid(username):
            return 1

        def mock_name_to_gid(groupname):
            return 2

        with mock.patch('salve.filesys.ConcreteFilesys.copy', mock_copy):
            with mock.patch('os.access', lambda x, y: True):
                dcp = copy.DirCopyAction('a',
                                         'b/c',
                                         self.dummy_file_context)
                dcp(ConcreteFilesys())

        mock_copy.assert_called_once_with('a', 'b/c')

    @istest
    def dircopy_unreadable_source_execute(self):
        """
        Unit: Directory Copy Action Execution, Unreadable Source
        """
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        unreadable_source_code = \
            copy.DirCopyAction.verification_codes.UNREADABLE_SOURCE
        with mock.patch('salve.action.copy.DirCopyAction.verify_can_exec',
                        lambda x, fs: unreadable_source_code):
            dcp = copy.DirCopyAction('a', 'b/c', self.dummy_file_context)
            dcp(ConcreteFilesys())

        err = self.stderr.getvalue()
        expected = ('[WARN] [EXECUTION] no such file: ' +
                    'DirCopy: Non-Readable source directory "a"\n')
        assert err == expected, "%s != %s" % (err, expected)

    @istest
    def dircopy_unwritable_target_execute(self):
        """
        Unit: Directory Copy Action Execution, Unwritable Target
        """
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        unwritable_target_code = \
            copy.DirCopyAction.verification_codes.UNWRITABLE_TARGET
        with mock.patch('salve.action.copy.DirCopyAction.verify_can_exec',
                        lambda x, fs: unwritable_target_code):
            dcp = copy.DirCopyAction('a', 'b/c', self.dummy_file_context)
            dcp(ConcreteFilesys())

        err = self.stderr.getvalue()
        expected = ('[WARN] [EXECUTION] no such file: ' +
                    'DirCopy: Non-Writable target directory "b/c"\n')
        assert err == expected, "%s != %s" % (err, expected)
