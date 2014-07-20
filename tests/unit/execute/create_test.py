#!/usr/bin/python

import os
import mock
from nose.tools import istest

from salve.util.context import SALVEContext, ExecutionContext, StreamContext

import salve.execute.action as action
import salve.execute.create as create
import tests.utils.scratch as scratch

_testfile_dir = os.path.join(os.path.dirname(__file__), 'files')


def get_full_path(filename):
    return os.path.join(_testfile_dir, filename)

dummy_stream_context = StreamContext('no such file', -1)
dummy_exec_context = ExecutionContext()
dummy_context = SALVEContext(stream_context=dummy_stream_context,
                             exec_context=dummy_exec_context)


class TestWithScratchdir(scratch.ScratchContainer):
    @istest
    def filecreate_execute(self):
        """
        File Create Action Execution
        Needs to be in a scratchdir to ensure that there is no file
        named 'a' in the target dir.
        """
        mock_open = mock.mock_open()
        a_name = self.get_fullname('a')

        with mock.patch('__builtin__.open', mock_open, create=True), \
             mock.patch('os.access', lambda x, y: True):
            fc = create.FileCreateAction(a_name, dummy_context)
            fc()

        mock_open.assert_called_once_with(a_name, 'w')
        handle = mock_open()
        assert len(handle.write.mock_calls) == 0

    @istest
    def dircreate_execute(self):
        """
        Directory Create Action Execution
        Needs to be in a scratchdir to ensure that there is no directory
        named 'a' in the target dir.
        """
        mock_mkdirs = mock.Mock()
        a_name = self.get_fullname('a')

        with mock.patch('os.makedirs', mock_mkdirs), \
             mock.patch('os.access', lambda x, y: True):
            dc = create.DirCreateAction(a_name, dummy_context)
            dc()

        mock_mkdirs.assert_called_once_with(a_name)


@istest
def filecreate_to_str():
    """
    File Create Action String Conversion
    """
    fc = create.FileCreateAction('a', dummy_context)

    assert str(fc) == ('FileCreateAction(dst=a,context=' +
                       str(dummy_context) + ')')


@istest
def dircreate_to_str():
    """
    Directory Create Action String Conversion
    """
    dc = create.DirCreateAction('a', dummy_context)

    assert str(dc) == ('DirCreateAction(dst=a,context=' +
                       str(dummy_context) + ')')
