#!/usr/bin/python

import os
import mock
from nose.tools import istest

from src.util.context import SALVEContext, ExecutionContext, StreamContext

import src.execute.action as action
import src.execute.copy as copy
import tests.utils.scratch as scratch

_testfile_dir = os.path.join(os.path.dirname(__file__), 'files')


def get_full_path(filename):
    return os.path.join(_testfile_dir, filename)

dummy_stream_context = StreamContext('no such file', -1)
dummy_exec_context = ExecutionContext()
dummy_context = SALVEContext(stream_context=dummy_stream_context,
                             exec_context=dummy_exec_context)


class TestWithScratchdir(scratch.ScratchContainer):
    def setUp(self):
        scratch.ScratchContainer.setUp(self)
        dummy_exec_context.set('run_log', self.stderr)

    @istest
    def filecopy_execute(self):
        """
        File Copy Action Execution
        """
        content = 'a b c d \n e f g'
        self.write_file('a', content)
        self.make_dir('b')
        a_name = self.get_fullname('a')
        b_name = self.get_fullname('b')

        fcp = copy.FileCopyAction(a_name,
                                  os.path.join(b_name, 'c'),
                                  dummy_context)
        fcp()

        assert content == self.read_file('b/c')

    @istest
    def canexec_unwritable_target(self):
        """
        File Copy Action Verify Unwritable Target
        Checks the results of a verification check when the target
        is an unwritable file.
        """
        content = 'abc'
        self.write_file('a', content)
        content = 'efg'
        self.write_file('b', content)
        a_name = self.get_fullname('a')
        b_name = self.get_fullname('b')

        os.chmod(b_name, 0444)
        fcp = copy.FileCopyAction(a_name, b_name,
                                  dummy_context)

        assert fcp.verify_can_exec() == \
                fcp.verification_codes.UNWRITABLE_TARGET

    @istest
    def canexec_unwritable_target_dir(self):
        """
        File Copy Action Verify Unwritable Target Directory
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

        os.chmod(b_name, 0000)
        fcp = copy.FileCopyAction(a_name, c_name,
                                  dummy_context)

        vcode = fcp.verify_can_exec()

        assert vcode == fcp.verification_codes.UNWRITABLE_TARGET

    @istest
    def canexec_unreadable_source(self):
        """
        File Copy Action Verify Unreadable Source
        Checks the results of a verification check when the source
        is an unreadable file.
        """
        content = 'abc'
        self.write_file('a', content)
        content = 'efg'
        self.write_file('b', content)
        a_name = self.get_fullname('a')
        b_name = self.get_fullname('b')

        os.chmod(a_name, 0000)
        fcp = copy.FileCopyAction(a_name, b_name,
                                  dummy_context)

        assert fcp.verify_can_exec() == \
                fcp.verification_codes.UNREADABLE_SOURCE

    @istest
    def dir_canexec_unwritable_target(self):
        """
        Dir Copy Action Verify Unwritable Target
        Checks the results of a verification check when the target
        is an unwritable directory.
        """
        self.make_dir('a')
        self.make_dir('b')

        a_name = self.get_fullname('a')
        b_name = self.get_fullname('b')
        os.chmod(b_name, 0444)

        c_name = self.get_fullname('b/c')
        dcp = copy.DirCopyAction(a_name, c_name,
                                  dummy_context)

        assert dcp.verify_can_exec() == \
                dcp.verification_codes.UNWRITABLE_TARGET

    @istest
    def filecopy_to_str(self):
        """
        File Copy Action String Conversion
        """
        fcp = copy.FileCopyAction('a',
                                  'b/c',
                                  dummy_context)

        assert str(fcp) == ('FileCopyAction(src=a,dst=b/c,context=' +
                            str(dummy_context) + ')')

    @istest
    def dircopy_to_str(self):
        """
        Directory Copy Action String Conversion
        """
        dcp = copy.DirCopyAction('a',
                                 'b/c',
                                 dummy_context)

        assert str(dcp) == ('DirCopyAction(src=a,dst=b/c,context=' +
                           str(dummy_context) + ')')

    @istest
    def dircopy_execute(self):
        """
        Directory Copy Action Execution
        """
        log = {
            'mock_cp': None
        }

        def mock_copytree(src, dst, symlinks=None):
            log['mock_cp'] = (src, dst, symlinks)

        def mock_name_to_uid(username):
            return 1

        def mock_name_to_gid(groupname):
            return 2

        with mock.patch('shutil.copytree', mock_copytree), \
             mock.patch('os.access', lambda x, y: True):
            dcp = copy.DirCopyAction('a',
                                      'b/c',
                                      dummy_context)
            dcp()

        assert log['mock_cp'] == ('a', 'b/c', True)

    @istest
    def dircopy_unwritable_target_execute(self):
        """
        Unit: Directory Copy Action Execution, Unwritable Target
        """
        unwritable_target_code = \
                copy.DirCopyAction.verification_codes.UNWRITABLE_TARGET
        with mock.patch('src.execute.copy.DirCopyAction.verify_can_exec',
                lambda x: unwritable_target_code):
            dcp = copy.DirCopyAction('a', 'b/c', dummy_context)
            dcp.execute()

        err = self.stderr.getvalue()
        expected = ('[WARN] [EXECUTION] no such file, line -1: ' +
                'DirCopy: Non-Writable target directory "b/c"\n')
        assert err == expected, "%s != %s" % (err, expected)
