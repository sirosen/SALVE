#!/usr/bin/python

import os
import mock
from nose.tools import istest, with_setup
from os.path import dirname, abspath, relpath

from salve import config, paths
from salve.exception import SALVEException

from tests.util import ensure_except, full_path

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


def make_mock_expanduser(env, user_to_home):
    """
    Given an environment and a map of usernames to home directories,
    produces a suitable mock for os.path.expanduser.
    """
    def mock_expanduser(string):
        for user in user_to_home:
            string = string.replace('~' + user, user_to_home[user])
        if string[0] == '~':
            string = user_to_home[env['USER']] + string[1:]
        return string

    return mock_expanduser


def setup_os1():
    """
    Setup the first dummy environment.
    """
    home_map = {'root': '/var/root',
                'user1': full_path('user1_homedir')}
    mock_env = {'SUDO_USER': 'user1',
               'USER': 'root',
               'HOME': home_map['user1']}

    # mock the expanduser function to use the mock env
    mock_expanduser = make_mock_expanduser(mock_env, home_map)
    expanduser_patch = mock.patch('os.path.expanduser', mock_expanduser)

    # mock group lookups to always return 'nogroup'
    mock_get_group = lambda x: 'nogroup'
    group_patch = mock.patch('salve.ugo.get_group_from_username',
                             mock_get_group)

    # put the patches in place
    setup_patches(mock.patch.dict('os.environ', mock_env),
                  group_patch,
                  expanduser_patch)


def setup_os2():
    home_map = {'root': '/var/root',
                'user1': full_path('user1_homedir')}
    mock_env = {'SUDO_USER': 'user1',
               'USER': 'root',
               'HOME': home_map['user1'],
               'SALVE_METADATA_PATH': '/etc/meta/'}

    # mock the expanduser function to use the mock env
    mock_expanduser = make_mock_expanduser(mock_env, home_map)
    expanduser_patch = mock.patch('os.path.expanduser', mock_expanduser)

    # mock group lookups to always return 'nogroup'
    mock_get_group = lambda x: 'nogroup'
    group_patch = mock.patch('salve.ugo.get_group_from_username',
                        mock_get_group)

    setup_patches(mock.patch.dict('os.environ', mock_env),
                  expanduser_patch,
                  group_patch)


def setup_os3():
    home_map = {'root': '/var/root',
                'user1': full_path('user1_homedir')}
    mock_env = {'SUDO_USER': 'user1',
               'USER': 'root',
               'HOME': home_map['user1'],
               'SALVE_META_DATA_PATH': '/etc/meta/'}

    # mock os.path
    mock_expanduser = make_mock_expanduser(mock_env, home_map)

    # mock group lookups to always return 'nogroup'
    mock_get_group = lambda x: 'nogroup'
    group_patch = mock.patch('salve.ugo.get_group_from_username',
                             mock_get_group)

    setup_patches(mock.patch.dict('os.environ', mock_env),
                  mock.patch('os.path.expanduser', mock_expanduser),
                  group_patch)


@istest
@with_setup(setup_os1, teardown_patches)
def sudo_user_replace():
    """
    Unit: Configuration SUDO_USER Replacement
    Tests the replacement of USER with SUDO_USER
    """
    orig_user = os.environ['USER']
    conf = config.SALVEConfig()
    assert conf.env['USER'] == 'user1'
    assert os.environ['USER'] == orig_user


@istest
@with_setup(setup_os1, teardown_patches)
def sudo_homedir_resolution():
    """
    Unit: Configuration HOME Replacement
    Tests the replacement of HOME with an expanded ~USER
    """
    orig_home = os.environ['HOME']
    conf = config.SALVEConfig()
    assert conf.env['HOME'] == full_path('user1_homedir')
    assert os.environ['HOME'] == orig_home


@istest
@with_setup(setup_os1, teardown_patches)
def valid_config1():
    """
    Unit: Configuration Valid Config File
    Tests that parsing a specified config file works.
    """
    conf = config.SALVEConfig(
            filename=full_path('single_section_single_attr.ini'))
    assert conf.attributes['metadata']['path'] == '/etc/salve-config/meta/'


@istest
@with_setup(setup_os1, teardown_patches)
def load_rc_file():
    """
    Unit: Configuration Load RC File
    Tests that, by default, the user's ~/.salverc is used for config.
    """
    conf = config.SALVEConfig()
    assert conf.attributes['metadata']['path'] == '/etc/salve-config/meta/'


@istest
@with_setup(setup_os2, teardown_patches)
def overload_from_env():
    """
    Unit: Configuration Overload From Environment
    Ensures that overloads in the environment take precedence over
    config file settings.
    """
    conf = config.SALVEConfig(
            filename=full_path('single_section_single_attr.ini'))
    assert conf.attributes['metadata']['path'] == '/etc/meta/'


@istest
@with_setup(setup_os3, teardown_patches)
def multiple_env_overload():
    """
    Unit: Configuration Multiple Overload From Environment Variable
    Checks that environment variables can be used to overload multiple
    settings if they happen to match badly. This is the expected
    behavior, as the alternatives are inconsistent and unpredictable.
    """
    conf = config.SALVEConfig(
            filename=full_path('two_sections.ini'))
    assert conf.attributes['meta_data']['path'] == '/etc/meta/'
    assert conf.attributes['meta']['data_path'] == '/etc/meta/'


@istest
@with_setup(setup_os1, teardown_patches)
def missing_config():
    """
    Unit: Configuration Missing Config File
    Checks that with a missing config file specified, the default is
    still loaded and works as if no config were specified.
    """
    conf = config.SALVEConfig(
            filename=full_path('NONEXISTENT_FILE'))

    assert conf.attributes['file']['action'] == 'copy'
    assert conf.attributes['file']['mode'] == '644'

    assert conf.attributes['directory']['action'] == 'copy'
    assert conf.attributes['directory']['mode'] == '755'

    assert conf.attributes['default']['user'] == '$USER'
    assert conf.attributes['default']['group'] == '$SALVE_USER_PRIMARY_GROUP'


@istest
@with_setup(setup_os1, teardown_patches)
def invalid_file():
    """
    Unit: Configuration Invalid Config File
    Checks that with a invalid config file specified, the ConfigParser
    error is converted into a SALVEException.
    """
    try:
        conf = config.SALVEConfig(
                filename=full_path('unassigned_val.ini'))
    except SALVEException as e:
        assert isinstance(e, SALVEException)
        assert ('Encountered an error while parsing' +
                ' your configuration file(s).') in e.message


@istest
@with_setup(setup_os1, teardown_patches)
def template_sub_keyerror():
    """
    Unit: Configuration Missing Variable
    Tests that templating throws an error when there is a nonexistent
    variable specified.
    """
    conf = config.SALVEConfig()
    ensure_except(KeyError, conf.template, '$NONEXISTENT_VAR')


@istest
@with_setup(setup_os1, teardown_patches)
def template_sub():
    """
    Unit: Configuration Variable Substitution
    Tests the normal functioning of variable substitution.
    """
    conf = config.SALVEConfig()
    assert conf.template('$USER') == 'user1'
    assert conf.template('$HOME') == full_path('user1_homedir')
    assert (conf.template('$HOME/bin/program') ==
            paths.pjoin(full_path('user1_homedir'), 'bin/program'))
