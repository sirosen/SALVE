#!/usr/bin/python

import lib.settings.settings as settings

from nose.tools import istest, with_setup
from mock import patch, Mock

import os
from os.path import dirname, join as pjoin

_testfile_dir = pjoin(dirname(__file__),'files')
_homes_dir = pjoin(dirname(__file__),'homes')
_active_patches = set()

def setup_patches(*patches):
    global _active_patches

    for p in patches:
        p.start()
        _active_patches.add(p)

def teardown_patches():
    global _active_patches
    for p in _active_patches:
        p.stop()
    _active_patches = set()

def make_mock_expanduser(env,user_to_home):
    def mock_expanduser(string):
        import sys
        for user in user_to_home:
            string = string.replace('~'+user,user_to_home[user])
        if string[0] == '~':
            string = user_to_home[env['USER']]+string[1:]
        return string

    return mock_expanduser

def setup_os1():
    home_map = {'root': '/var/root',
                'user1': pjoin(_homes_dir,'user1')}
    mock_env= {'SUDO_USER': 'user1',
               'USER': 'root',
               'HOME': home_map['user1']}
    mock_path = Mock()
    mock_path.expanduser = make_mock_expanduser(mock_env,home_map)
    mock_path.join = pjoin

    setup_patches(patch.dict('os.environ',mock_env),
                  patch('os.path',mock_path))

def setup_os2():
    home_map = {'root': '/var/root',
                'user1': pjoin(_homes_dir,'user1')}
    mock_env= {'SUDO_USER': 'user1',
               'USER': 'root',
               'HOME': home_map['user1'],
               'SALVE_METADATA_PATH': '/etc/meta/'}
    mock_path = Mock()
    mock_path.expanduser = make_mock_expanduser(mock_env,home_map)
    mock_path.join = pjoin

    setup_patches(patch.dict('os.environ',mock_env),
                  patch('os.path',mock_path))

def setup_os3():
    home_map = {'root': '/var/root',
                'user1': pjoin(_homes_dir,'user1')}
    mock_env= {'SUDO_USER': 'user1',
               'USER': 'root',
               'HOME': home_map['user1'],
               'SALVE_META_DATA_PATH': '/etc/meta/'}
    mock_path = Mock()
    mock_path.expanduser = make_mock_expanduser(mock_env,home_map)
    mock_path.join = pjoin

    setup_patches(patch.dict('os.environ',mock_env),
                  patch('os.path',mock_path))


@istest
@with_setup(setup_os1,teardown_patches)
def sudo_user_replace():
    """
    Checks that invocations with sudo correctly set the value
    of USER inside of the configuration object, but don't effect
    os.environ
    """
    orig_user = os.environ['USER']
    conf = settings.SALVEConfig()
    assert conf.env['USER'] == 'user1'
    assert os.environ['USER'] == orig_user

@istest
@with_setup(setup_os1,teardown_patches)
def sudo_homedir_resolution():
    """
    Checks that invocations with sudo correctly set the value
    of HOME inside of the configuration object, but don't effect
    os.environ
    """
    orig_home = os.environ['HOME']
    conf = settings.SALVEConfig()
    assert conf.env['HOME'] == pjoin(_homes_dir,'user1')
    assert os.environ['HOME'] == orig_home

@istest
@with_setup(setup_os1,teardown_patches)
def valid_config1():
    """
    Checks that a valid ini file is parsed and stored correctly.
    """
    conf = settings.SALVEConfig(pjoin(_testfile_dir,'valid1.ini'))
    assert conf.attributes['metadata']['path'] == '/etc/salve-config/meta/'

@istest
@with_setup(setup_os1,teardown_patches)
def load_rc_file():
    """
    Checks that in the absence of an explicit config file, we still
    load the user's ~/.salverc file.
    """
    conf = settings.SALVEConfig()
    assert conf.attributes['metadata']['path'] == '/etc/salve-config/meta/'

@istest
@with_setup(setup_os2,teardown_patches)
def overload_from_env():
    """
    Checks that environment variables can be used to overload values
    loaded from config.
    """
    conf = settings.SALVEConfig(pjoin(_testfile_dir,'valid1.ini'))
    assert conf.attributes['metadata']['path'] == '/etc/meta/'

@istest
@with_setup(setup_os3,teardown_patches)
def multiple_env_overload():
    """
    Checks that a single environment variable overloads _all_ matching
    attributes, not just the first one.
    """
    conf = settings.SALVEConfig(pjoin(_testfile_dir,'valid2.ini'))
    assert conf.attributes['meta_data']['path'] == '/etc/meta/'
    assert conf.attributes['meta']['data_path'] == '/etc/meta/'

@istest
@with_setup(setup_os1,teardown_patches)
def missing_config():
    """
    Checks that a missing config file does not raise any errors.
    """
    settings.SALVEConfig(pjoin(_testfile_dir,'NONEXISTENT_FILE'))

@istest
@with_setup(setup_os1,teardown_patches)
def template_sub_keyerror():
    """
    Checks that an unknown identifier in a template string triggers a
    KeyError.
    """
    conf = settings.SALVEConfig()
    try:
        conf.template('$NONEXISTENT_VAR')
        assert False
    except KeyError:
        pass
    else:
        assert False

@istest
@with_setup(setup_os1,teardown_patches)
def template_sub():
    """
    Checks that template string substitutions on strings with known,
    valid identifiers work correctly.
    """
    conf = settings.SALVEConfig()
    assert conf.template('$USER') == 'user1'
    assert conf.template('$HOME') == pjoin(_homes_dir,'user1')
    assert conf.template('$HOME/bin/program') == pjoin(_homes_dir,'user1','bin/program')
