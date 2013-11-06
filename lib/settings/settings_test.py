#!/usr/bin/python

from __future__ import print_function
import settings

from nose.tools import istest, with_setup
from mock import patch, Mock

_active_patches = []

def setup_os1():
    global _active_patches
    mock_environ = {'SUDO_USER': 'user1',
                    'USER': 'root',
                    'HOME': '/home/user1'}
    def mock_expanduser(string):
        import sys
        string = string.replace('~user1','/home/user1')
        string = string.replace('~root','/var/root')
        if string[0] == '~': string = '/home/user1'+string[1:]
        return string
    mock_path = Mock()
    mock_path.expanduser = mock_expanduser

    _active_patches.append(patch.dict('os.environ',mock_environ))
    _active_patches.append(patch('os.path',mock_path))

    for p in _active_patches:
        p.start()

def teardown_os():
    global _active_patches
    for p in _active_patches:
        p.stop()
    _active_patches = []

@istest
@with_setup(setup_os1,teardown_os)
def sudo_user_replace():
    conf = settings.SALVEConfig()
    assert conf.env['USER'] == 'user1'

@istest
@with_setup(setup_os1,teardown_os)
def sudo_homedir_resolution():
    conf = settings.SALVEConfig()
    assert conf.env['HOME'] == '/home/user1'
