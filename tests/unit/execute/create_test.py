#!/usr/bin/python

import os
import mock
from nose.tools import istest

from src.util.error import StreamContext

import src.execute.action as action
import src.execute.create as create

_testfile_dir = os.path.join(os.path.dirname(__file__),'files')
def get_full_path(filename):
    return os.path.join(_testfile_dir,filename)

dummy_context = StreamContext('no such file',-1)

@istest
def filecreate_to_str():
    """
    File Create Action String Conversion
    """
    fc = create.FileCreateAction('a',dummy_context)

    assert str(fc) == 'FileCreateAction(dst=a,context='+\
                       str(dummy_context)+')'

@istest
def filecreate_execute():
    """
    File Create Action Execution
    """
    mock_open = mock.mock_open()

    with mock.patch('__builtin__.open',mock_open,create=True), \
         mock.patch('os.access', lambda x,y: True):
        fc = create.FileCreateAction('a', dummy_context)
        fc()

    mock_open.assert_called_once_with('a','w')
    handle = mock_open()
    assert len(handle.write.mock_calls) == 0

@istest
def dircreate_to_str():
    """
    Directory Create Action String Conversion
    """
    dc = create.DirCreateAction('a',dummy_context)

    assert str(dc) == 'DirCreateAction(dst=a,context='+\
                       str(dummy_context)+')'

@istest
def dircreate_execute():
    """
    Directory Create Action Execution
    """
    mock_mkdirs = mock.Mock()

    with mock.patch('os.makedirs',mock_mkdirs), \
         mock.patch('os.access', lambda x,y: True):
        dc = create.DirCreateAction('a', dummy_context)
        dc()

    mock_mkdirs.assert_called_once_with('a')
