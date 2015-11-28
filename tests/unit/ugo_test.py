import mock
from nose.tools import istest, eq_
from nose_parameterized import parameterized

from tests.framework import first_param_docfunc

from salve import ugo


@istest
@mock.patch('pwd.getpwnam')
@mock.patch('grp.getgrgid')
def group_from_username(mock_getgrgid, mock_getpwnam):
    """
    Unit: Fetch Group From Username

    Tests the behavior of get_group_from_username using mocked values
    for getpwnam and getgrgid.
    """
    mock_getgrgid.return_value.gr_name = 'group1'
    mock_getpwnam.return_value.pw_gid = 21

    eq_(ugo.get_group_from_username('user1'), 'group1')

    mock_getgrgid.assert_called_once_with(21)
    mock_getpwnam.assert_called_once_with('user1')


@parameterized.expand(
    [('Unit: Check Root Status (True)', 0, True),
     ('Unit: Check Root Status (False)', 1, False)],
    testcase_func_doc=first_param_docfunc)
@istest
@mock.patch('os.geteuid')
def is_root_check(description, euid, isroot, mock_geteuid):
    """
    Confirms that is_root matches the result of os.geteuid.
    """
    mock_geteuid.return_value = euid
    eq_(ugo.is_root(), isroot)


@istest
@mock.patch('pwd.getpwnam')
def name_to_uid(mock_getpwnam):
    """
    Unit: UID From Username

    Checks the result of name_to_uid using getpwnam.
    """
    mock_getpwnam.return_value.pw_uid = 101

    eq_(ugo.name_to_uid('user1'), 101)
    mock_getpwnam.assert_called_once_with('user1')


@istest
@mock.patch('grp.getgrnam')
def name_to_gid(mock_getgrnam):
    """
    Unit: GID From Username

    Checks the result of name_to_gid using getgrnam.
    """
    mock_getgrnam.return_value.gr_gid = 2000

    eq_(ugo.name_to_gid('group2'), 2000)
    mock_getgrnam.assert_called_once_with('group2')
