#!/usr/bin/python

import os
import mock
from nose.tools import istest

from salve.context import ExecutionContext, FileContext

from salve.action import create
from salve.filesys import real_fs
from tests.util import scratch

dummy_file_context = FileContext('no such file')
dummy_exec_context = ExecutionContext()


class TestWithScratchdir(scratch.ScratchContainer):
    @istest
    def filecreate_execute(self):
        """
        Unit: File Create Action Execution
        Needs to be in a scratchdir to ensure that there is no file
        named 'a' in the target dir.
        """
        mock_open = mock.mock_open()
        a_name = self.get_fullname('a')

        try:
            import builtins
            builtin_patch = mock.patch('builtins.open', mock_open, create=True)
        except ImportError:
            import __builtin__ as builtins
            builtin_patch = mock.patch('__builtin__.open', mock_open,
                    create=True)

        with builtin_patch:
            with mock.patch('os.access', lambda x, y: True):
                fc = create.FileCreateAction(a_name, dummy_file_context)
                fc(real_fs)

        mock_open.assert_called_once_with(a_name, 'a')
        handle = mock_open()
        assert len(handle.write.mock_calls) == 0

    @istest
    def dircreate_execute(self):
        """
        Unit: Directory Create Action Execution
        Needs to be in a scratchdir to ensure that there is no directory
        named 'a' in the target dir.
        """
        mock_mkdirs = mock.Mock()
        a_name = self.get_fullname('a')

        with mock.patch('os.makedirs', mock_mkdirs):
            with mock.patch('os.access', lambda x, y: True):
                dc = create.DirCreateAction(a_name, dummy_file_context)
                dc(real_fs)

        mock_mkdirs.assert_called_once_with(a_name)


@istest
def filecreate_to_str():
    """
    Unit: File Create Action String Conversion
    """
    fc = create.FileCreateAction('a', dummy_file_context)

    assert str(fc) == ('FileCreateAction(dst=a,context=' +
                       repr(dummy_file_context) + ')')


@istest
def dircreate_to_str():
    """
    Unit: Directory Create Action String Conversion
    """
    dc = create.DirCreateAction('a', dummy_file_context)

    assert str(dc) == ('DirCreateAction(dst=a,context=' +
                       repr(dummy_file_context) + ')')
