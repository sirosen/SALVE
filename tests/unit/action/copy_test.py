import os
import mock
from nose.tools import istest

from salve.context import FileContext

from salve.action import copy
from salve.filesys import ConcreteFilesys
from tests.framework import scratch, assert_substr

from .helpers import verification_produces_code


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
    def verify_fails_generator(self):
        parameters = [
            ('rw_file_1', 'r_only_file_1',
             'UNWRITABLE_TARGET', copy.FileCopyAction,
             'Unit: File Copy Action Verify Unwritable Target'),
            ('rw_file_1', 'no_perms_dir_1/otherfile',
             'UNWRITABLE_TARGET', copy.FileCopyAction,
             'Unit: File Copy Action Verify Unwritable Target Directory'),
            ('no_perms_file_1', 'rw_file_1',
             'UNREADABLE_SOURCE', copy.FileCopyAction,
             'Unit: File Copy Action Verify Unreadable Source'),
            ('no_perms_file_1', 'rw_file_1',
             'UNREADABLE_SOURCE', copy.FileCopyAction,
             'Unit: File Copy Action Verify Unreadable Source'),
            ('no_perms_dir_1', 'rw_dir_1',
             'UNREADABLE_SOURCE', copy.DirCopyAction,
             'Unit: Dir Copy Action Verify Unreadable Source'),
            ('rw_dir_1', 'no_perms_dir_1/abc',
             'UNWRITABLE_TARGET', copy.DirCopyAction,
             'Unit: Dir Copy Action Verify Unwritable Target'),
        ]

        for (src, dst, code, klass, description) in parameters:
            def check_func():
                act = klass(self.get_fullname(src), self.get_fullname(dst),
                            self.dummy_file_context)
                verification_produces_code(act, code)
            check_func.description = description

            yield check_func

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
    def dircopy_execute_failure_generator(self):
        parameters = [
            ('UNREADABLE_SOURCE',
             ('EXECUTION [WARNING] no such file: ' +
              'DirCopy: Non-Readable source directory "a"\n'),
             'Unit: Directory Copy Action Execution, Unreadable Source'),
            ('UNWRITABLE_TARGET',
             ('EXECUTION [WARNING] no such file: ' +
              'DirCopy: Non-Writable target directory "b/c"\n'),
             'Unit: Directory Copy Action Execution, Unwritable Target'),
        ]

        for (code, expected_err, description) in parameters:
            @mock.patch('salve.action.copy.DirCopyAction.verify_can_exec',
                        lambda self, fs: self.verification_codes[code])
            def check_func():
                dcp = copy.DirCopyAction('a', 'b/c', self.dummy_file_context)
                dcp(ConcreteFilesys())

                err = self.stderr.getvalue()
                assert_substr(expected_err, err)
            check_func.description = description

            yield check_func
