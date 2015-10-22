#!/usr/bin/python

import os
import mock
from nose.tools import istest

from salve.context import ExecutionContext, FileContext

from salve.action import copy
from salve.filesys import ConcreteFilesys
from tests.util import scratch, assert_substr


class TestWithScratchdir(scratch.ScratchContainer):
    def __init__(self):
        scratch.ScratchContainer.__init__(self)
        self.dummy_file_context = FileContext('no such file')

        # a whole lot of file setup in the scratch dir
        self.write_file('rw_file_1', 'file with R and W perms')
        self.make_dir('rw_dir_1')
        self.write_file('r_only_file_1', 'file with only R perms')
        os.chmod(self.get_fullname('r_only_file_1'), 0o444)
        self.make_dir('no_perms_dir_1')
        os.chmod(self.get_fullname('no_perms_dir_1'), 0o000)
        self.write_file('no_perms_file_1', 'file with no allowed perms')
        os.chmod(self.get_fullname('no_perms_file_1'), 0o000)

    @istest
    def filecopy_execute(self):
        """
        Unit: File Copy Action Execution
        """
        fcp = copy.FileCopyAction(
            self.get_fullname('rw_file_1'),
            os.path.join(self.get_fullname('rw_dir_1'), 'c'),
            self.dummy_file_context)
        fcp(ConcreteFilesys())

        assert self.read_file('rw_file_1') == self.read_file('rw_dir_1/c')

    @istest
    def canexec_unwritable_target(self):
        """
        Unit: File Copy Action Verify Unwritable Target
        Checks the results of a verification check when the target
        is an unwritable file.
        """
        fcp = copy.FileCopyAction(self.get_fullname('rw_file_1'),
                                  self.get_fullname('r_only_file_1'),
                                  self.dummy_file_context)

        assert (fcp.verify_can_exec(ConcreteFilesys()) ==
                fcp.verification_codes.UNWRITABLE_TARGET)

    @istest
    def canexec_unwritable_target_dir(self):
        """
        Unit: File Copy Action Verify Unwritable Target Directory
        Checks the results of a verification check when the target
        is in an unwritable directory.
        """
        fcp = copy.FileCopyAction(
            self.get_fullname('rw_file_1'),
            self.get_fullname('no_perms_dir_1/otherfile'),
            self.dummy_file_context)

        assert (fcp.verify_can_exec(ConcreteFilesys()) ==
                fcp.verification_codes.UNWRITABLE_TARGET)

    @istest
    def canexec_unreadable_source(self):
        """
        Unit: File Copy Action Verify Unreadable Source
        Checks the results of a verification check when the source
        is an unreadable file.
        """
        fcp = copy.FileCopyAction(self.get_fullname('no_perms_file_1'),
                                  self.get_fullname('rw_file_1'),
                                  self.dummy_file_context)

        assert (fcp.verify_can_exec(ConcreteFilesys()) ==
                fcp.verification_codes.UNREADABLE_SOURCE)

    @istest
    def dir_canexec_unreadable_source(self):
        """
        Unit: Dir Copy Action Verify Unreadable Source
        Checks the results of a verification check when the source
        is an unreadable dir.
        """
        dcp = copy.DirCopyAction(self.get_fullname('no_perms_dir_1'),
                                 self.get_fullname('rw_dir_1'),
                                 self.dummy_file_context)

        assert (dcp.verify_can_exec(ConcreteFilesys()) ==
                dcp.verification_codes.UNREADABLE_SOURCE)

    @istest
    def dir_canexec_unwritable_target(self):
        """
        Unit: Dir Copy Action Verify Unwritable Target
        Checks the results of a verification check when the target
        is an unwritable directory.
        """
        dcp = copy.DirCopyAction(self.get_fullname('rw_dir_1'),
                                 self.get_fullname('no_perms_dir_1/abc'),
                                 self.dummy_file_context)

        assert (dcp.verify_can_exec(ConcreteFilesys()) ==
                dcp.verification_codes.UNWRITABLE_TARGET)

    @istest
    def stringification_test_generator(self):
        class_tuples = [(copy.FileCopyAction, 'FileCopyAction'),
                        (copy.DirCopyAction, 'DirCopyAction')]

        for (klass, name) in class_tuples:
            def check_func():
                act = klass('a', 'b/c', self.dummy_file_context)
                assert str(act) == '{0}(src=a,dst=b/c,context={1})'.format(
                    name, repr(self.dummy_file_context))
            check_func.description = "Unit: {0} String Conversion".format(name)

            yield check_func

    @istest
    @mock.patch('os.access', lambda x, y: True)
    @mock.patch('salve.filesys.ConcreteFilesys.copy')
    def dircopy_execute(self, mock_copy):
        """
        Unit: Directory Copy Action Execution
        """
        dcp = copy.DirCopyAction('a', 'b/c', self.dummy_file_context)
        dcp(ConcreteFilesys())

        mock_copy.assert_called_once_with('a', 'b/c')

    @istest
    @mock.patch('salve.action.copy.DirCopyAction.verify_can_exec',
                lambda self, fs: self.verification_codes.UNREADABLE_SOURCE)
    def dircopy_unreadable_source_execute(self):
        """
        Unit: Directory Copy Action Execution, Unreadable Source
        """
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION,
                                      quiet=True)

        dcp = copy.DirCopyAction('a', 'b/c', self.dummy_file_context)
        dcp(ConcreteFilesys())

        err = self.stderr.getvalue()
        expected = ('EXECUTION [WARNING] no such file: ' +
                    'DirCopy: Non-Readable source directory "a"\n')
        assert_substr(expected, err)

    @istest
    @mock.patch('salve.action.copy.DirCopyAction.verify_can_exec',
                lambda self, fs: self.verification_codes.UNWRITABLE_TARGET)
    def dircopy_unwritable_target_execute(self):
        """
        Unit: Directory Copy Action Execution, Unwritable Target
        """
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION,
                                      quiet=True)

        dcp = copy.DirCopyAction('a', 'b/c', self.dummy_file_context)
        dcp(ConcreteFilesys())

        err = self.stderr.getvalue()
        expected = ('EXECUTION [WARNING] no such file: ' +
                    'DirCopy: Non-Writable target directory "b/c"\n')
        assert_substr(expected, err)
