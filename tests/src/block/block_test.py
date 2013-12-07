#!/usr/bin/python

from nose.tools import istest
import os, mock
from tests.utils.exceptions import ensure_except

import src.block.base
import src.settings.config

_testfile_dir = os.path.join(os.path.dirname(__file__),'files')
def get_full_path(filename):
    return os.path.join(_testfile_dir,filename)

def mock_expanduser(string):
    user = os.environ['USER']
    string = string.replace('~'+user,_testfile_dir)
    if string[0] == '~':
        string = _testfile_dir+string[1:]
    return string

_dummy_conf = None
with mock.patch('os.path.expanduser',mock_expanduser):
    _dummy_conf = src.settings.config.SALVEConfig()

@istest
def block_is_abstract():
    """
    Block Base Class Is Abstract
    Ensures that a Block cannot be instantiated.
    """
    ensure_except(TypeError,src.block.base.Block)
