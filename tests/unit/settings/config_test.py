#!/usr/bin/python

import os
import mock
from nose.tools import istest, with_setup
from os.path import dirname, abspath, join as pjoin

from tests.utils.exceptions import ensure_except

import src.settings.config as config

_testfile_dir = pjoin(dirname(__file__),'files')
_homes_dir = pjoin(dirname(__file__),'homes')
_active_patches = set()

def setup_patches(*patches):
    """
    Puts a set of globally visible patches in place.
    """
    global _active_patches

    for p in patches:
        p.start()
        _active_patches.add(p)

def teardown_patches():
    """
    Removes the globally known patches.
    """
    global _active_patches
    for p in _active_patches:
        p.stop()
    _active_patches = set()

def make_mock_expanduser(env,user_to_home):
    """
    Given an environment and a map of usernames to home directories,
    produces a suitable mock for os.path.expanduser.
    """
    def mock_expanduser(string):
        for user in user_to_home:
            string = string.replace('~'+user,user_to_home[user])
        if string[0] == '~':
            string = user_to_home[env['USER']]+string[1:]
        return string

    return mock_expanduser

def setup_os1():
    """
    Setup the first dummy environment.
    """
    home_map = {'root': '/var/root',
                'user1': pjoin(_homes_dir,'user1')}
    mock_env= {'SUDO_USER': 'user1',
               'USER': 'root',
               'HOME': home_map['user1']}

    # mock the whole os.path module
    mock_path = mock.Mock()
    mock_path.expanduser = make_mock_expanduser(mock_env,home_map)
    mock_path.join = pjoin
    mock_path.dirname = dirname
    mock_path.abspath = abspath

    # mock group lookups to always return 'nogroup'
    mock_get_group = lambda x: 'nogroup'
    group_patch = mock.patch('src.util.ugo.get_group_from_username',
                             mock_get_group)

    # put the patches in place
    setup_patches(mock.patch.dict('os.environ',mock_env),
                  mock.patch('os.path',mock_path),
                  group_patch)

def setup_os2():
    home_map = {'root': '/var/root',
                'user1': pjoin(_homes_dir,'user1')}
    mock_env= {'SUDO_USER': 'user1',
               'USER': 'root',
               'HOME': home_map['user1'],
               'SALVE_METADATA_PATH': '/etc/meta/'}

    # mock os.path
    mock_path = mock.Mock()
    mock_path.expanduser = make_mock_expanduser(mock_env,home_map)
    mock_path.join = pjoin
    mock_path.dirname = dirname
    mock_path.abspath = abspath

    # mock group lookups to always return 'nogroup'
    mock_get_group = lambda x: 'nogroup'
    group_patch = mock.patch('src.util.ugo.get_group_from_username',
                        mock_get_group)

    setup_patches(mock.patch.dict('os.environ',mock_env),
                  mock.patch('os.path',mock_path),
                  group_patch)

def setup_os3():
    home_map = {'root': '/var/root',
                'user1': pjoin(_homes_dir,'user1')}
    mock_env= {'SUDO_USER': 'user1',
               'USER': 'root',
               'HOME': home_map['user1'],
               'SALVE_META_DATA_PATH': '/etc/meta/'}

    # mock os.path
    mock_path = mock.Mock()
    mock_path.expanduser = make_mock_expanduser(mock_env,home_map)
    mock_path.join = pjoin
    mock_path.dirname = dirname
    mock_path.abspath = abspath

    # mock group lookups to always return 'nogroup'
    mock_get_group = lambda x: 'nogroup'
    group_patch = mock.patch('src.util.ugo.get_group_from_username',
                             mock_get_group)

    setup_patches(mock.patch.dict('os.environ',mock_env),
                  mock.patch('os.path',mock_path),
                  group_patch)


@istest
@with_setup(setup_os1,teardown_patches)
def sudo_user_replace():
    """
    Configuration SUDO_USER Replacement
    Tests the replacement of USER with SUDO_USER
    """
    orig_user = os.environ['USER']
    conf = config.SALVEConfig()
    assert conf.env['USER'] == 'user1'
    assert os.environ['USER'] == orig_user

@istest
@with_setup(setup_os1,teardown_patches)
def sudo_homedir_resolution():
    """
    Configuration HOME Replacement
    Tests the replacement of HOME with an expanded ~USER
    """
    orig_home = os.environ['HOME']
    conf = config.SALVEConfig()
    assert conf.env['HOME'] == pjoin(_homes_dir,'user1')
    assert os.environ['HOME'] == orig_home

@istest
@with_setup(setup_os1,teardown_patches)
def valid_config1():
    """
    Configuration Valid Config File
    Tests that parsing a specified config file works.
    """
    conf = config.SALVEConfig(pjoin(_testfile_dir,'valid1.ini'))
    assert conf.attributes['metadata']['path'] == '/etc/salve-config/meta/'

@istest
@with_setup(setup_os1,teardown_patches)
def load_rc_file():
    """
    Configuration Load RC File
    Tests that, by default, the user's ~/.salverc is used for config.
    """
    conf = config.SALVEConfig()
    assert conf.attributes['metadata']['path'] == '/etc/salve-config/meta/'

@istest
@with_setup(setup_os2,teardown_patches)
def overload_from_env():
    """
    Configuration Overload From Environment
    Ensures that overloads in the environment take precedence over
    config file settings.
    """
    conf = config.SALVEConfig(pjoin(_testfile_dir,'valid1.ini'))
    assert conf.attributes['metadata']['path'] == '/etc/meta/'

@istest
@with_setup(setup_os3,teardown_patches)
def multiple_env_overload():
    """
    Configuration Multiple Overload From Environment Variable
    Checks that environment variables can be used to overload multiple
    settings if they happen to match badly. This is the expected
    behavior, as the alternatives are inconsistent and unpredictable.
    """
    conf = config.SALVEConfig(pjoin(_testfile_dir,'valid2.ini'))
    assert conf.attributes['meta_data']['path'] == '/etc/meta/'
    assert conf.attributes['meta']['data_path'] == '/etc/meta/'

@istest
@with_setup(setup_os1,teardown_patches)
def missing_config():
    """
    Configuration Missing Config File
    Checks that with a missing config file specified, the default is
    still loaded and works as if no config were specified.
    """
    conf = config.SALVEConfig(pjoin(_testfile_dir,'NONEXISTENT_FILE'))

    assert conf.attributes['file']['action'] == 'copy'
    assert conf.attributes['file']['mode'] == '600'
    assert conf.attributes['file']['user'] == '$USER'

    assert conf.attributes['directory']['action'] == 'copy'
    assert conf.attributes['directory']['mode'] == '755'
    assert conf.attributes['directory']['user'] == '$USER'

@istest
@with_setup(setup_os1,teardown_patches)
def template_sub_keyerror():
    """
    Configuration Missing Variable
    Tests that templating throws an error when there is a nonexistent
    variable specified.
    """
    conf = config.SALVEConfig()
    ensure_except(KeyError,conf.template,'$NONEXISTENT_VAR')

@istest
@with_setup(setup_os1,teardown_patches)
def template_sub():
    """
    Configuration Variable Substitution
    Tests the normal functioning of variable substitution.
    """
    conf = config.SALVEConfig()
    assert conf.template('$USER') == 'user1'
    assert conf.template('$HOME') == pjoin(_homes_dir,'user1')
    assert conf.template('$HOME/bin/program') == pjoin(_homes_dir,'user1','bin/program')