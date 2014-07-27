#!/usr/bin/python

import salve.util.ugo as ugo

from nose.tools import istest
import mock

from collections import namedtuple


@istest
def group_from_username():
    """
    Unit: Fetch Group From Username

    Tests the behavior of get_group_from_username using mocked values
    for getpwnam and getgrgid.
    """
    mock_getgrgid = mock.Mock()
    mock_group = namedtuple('mock_group', ['gr_name'])
    mock_getgrgid.return_value = mock_group('group1')

    mock_getpwnam = mock.Mock()
    mock_pw = namedtuple('mock_pw', ['pw_gid'])
    mock_getpwnam.return_value = mock_pw(21)

    with mock.patch('pwd.getpwnam', mock_getpwnam):
        with mock.patch('grp.getgrgid', mock_getgrgid):
            grp = ugo.get_group_from_username('user1')

    assert grp == 'group1'
    mock_getgrgid.assert_called_once_with(21)
    mock_getpwnam.assert_called_once_with('user1')


@istest
def is_root_check():
    """
    Unit: Check Root Status

    Confirms that is_root matches the result of os.geteuid.
    """
    mock_geteuid = mock.Mock()

    mock_geteuid.return_value = 0
    with mock.patch('os.geteuid', mock_geteuid):
        root_status = ugo.is_root()
    assert root_status

    mock_geteuid.return_value = 1
    with mock.patch('os.geteuid', mock_geteuid):
        root_status = ugo.is_root()
    assert not root_status


@istest
def name_to_uid():
    """
    Unit: UUID From Username

    Checks the result of name_to_uid using getpwnam.
    """
    mock_pw = namedtuple('mock_pw', ['pw_uid'])
    mock_getpwnam = mock.Mock()
    mock_getpwnam.return_value = mock_pw(101)

    with mock.patch('pwd.getpwnam', mock_getpwnam):
        uuid = ugo.name_to_uid('user1')

    assert uuid == 101
    mock_getpwnam.assert_called_once_with('user1')


@istest
def name_to_gid():
    """
    Unit: GID From Username

    Checks the result of name_to_gid using getgrnam.
    """
    mock_gr = namedtuple('mock_gr', ['gr_gid'])
    mock_getgrnam = mock.Mock()
    mock_getgrnam.return_value = mock_gr(2000)

    with mock.patch('grp.getgrnam', mock_getgrnam):
        gid = ugo.name_to_gid('group2')

    assert gid == 2000
    mock_getgrnam.assert_called_once_with('group2')
