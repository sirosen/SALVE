import os

import mock
from nose.tools import istest, eq_
from nose_parameterized import parameterized
from tests.framework import scratch, assert_substr, first_param_docfunc

from salve.action import copy
from salve.filesys import ConcreteFilesys
from salve.context import ExecutionContext, FileContext

from .helpers import verification_produces_code


class TestWithScratchdir(scratch.ScratchContainer):
    def __init__(self):
        scratch.ScratchContainer.__init__(self)
        self.dummy_file_context = FileContext('no such file')

    def setUp(self):
        scratch.ScratchContainer.setUp(self)

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

    @parameterized.expand(
        [('Unit: File Copy Action Verify Unwritable Target',
          'rw_file_1', 'r_only_file_1', 'UNWRITABLE_TARGET',
          copy.FileCopyAction),
         ('Unit: File Copy Action Verify Unwritable Target Directory',
          'rw_file_1', 'no_perms_dir_1/otherfile', 'UNWRITABLE_TARGET',
          copy.FileCopyAction),
         ('Unit: File Copy Action Verify Unreadable Source',
          'no_perms_file_1', 'rw_file_1', 'UNREADABLE_SOURCE',
          copy.FileCopyAction),
         ('Unit: File Copy Action Verify Unreadable Source',
          'no_perms_file_1', 'rw_file_1', 'UNREADABLE_SOURCE',
          copy.FileCopyAction),
         ('Unit: Dir Copy Action Verify Unreadable Source',
          'no_perms_dir_1', 'rw_dir_1', 'UNREADABLE_SOURCE',
          copy.DirCopyAction),
         ('Unit: Dir Copy Action Verify Unwritable Target',
          'rw_dir_1', 'no_perms_dir_1/abc', 'UNWRITABLE_TARGET',
          copy.DirCopyAction),
         ],
        testcase_func_doc=first_param_docfunc)
    @istest
    def verify_copy_fails(self, description, src, dst, code, klass):
        act = klass(self.get_fullname(src), self.get_fullname(dst),
                    self.dummy_file_context)
        verification_produces_code(act, code)

    @parameterized.expand(
        [('Unit: FileCopyAction String Conversion',
          'FileCopyAction', copy.FileCopyAction),
         ('Unit: DirCopyAction String Conversion',
          'DirCopyAction', copy.DirCopyAction)],
        testcase_func_doc=first_param_docfunc)
    @istest
    def copy_action_stringification(self, description, name, klass):
        act = klass('a', 'b/c', self.dummy_file_context)
        eq_(str(act), '{0}(src=a,dst=b/c,context={1!r})'
                      .format(name, self.dummy_file_context))

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

    @parameterized.expand(
        [('Unit: Directory Copy Action Execution, Unreadable Source',
          'UNREADABLE_SOURCE',
          ('EXECUTION [WARNING] no such file: ' +
           'DirCopy: Non-Readable source directory "a"')),
         ('Unit: Directory Copy Action Execution, Unwritable Target',
          'UNWRITABLE_TARGET',
          ('EXECUTION [WARNING] no such file: ' +
           'DirCopy: Non-Writable target directory "b/c"'))],
        testcase_func_doc=first_param_docfunc)
    @istest
    def dircopy_execute_failure(self, description, code, expected_err):
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION,
                                      quiet=True)

        with mock.patch('salve.action.copy.DirCopyAction.verify_can_exec',
                        lambda self, fs: self.verification_codes[code]):
            dcp = copy.DirCopyAction('a', 'b/c', self.dummy_file_context)
            dcp(ConcreteFilesys())

            err = self.stderr.getvalue()
            assert_substr(err, expected_err)
