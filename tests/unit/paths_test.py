import mock
from nose.tools import istest, eq_, ok_

from salve import paths


@istest
def get_default_config():
    """
    Unit: Paths Get Default Config File
    Tests finding the settings ini file.
    This is, like the SALVE root, always relative to paths.__file__
    """
    with mock.patch('salve.paths.__file__',
                    '/tmp/salve/paths.py'):
        eq_(paths.get_default_config(), '/tmp/salve/default_settings.ini')


@istest
def identify_abspath():
    """
    Unit: Paths Identify Absolute Path
    Tests that the paths module can successfully identify an absolute
    path as such.
    """
    ok_(paths.is_abs_or_var('/a'))
    ok_(paths.is_abs_or_var('/a/b/c'))
    ok_(paths.is_abs_or_var('/../a/b/c'))

    ok_(not paths.is_abs_or_var('a'))
    ok_(not paths.is_abs_or_var('a/b/c'))
    ok_(not paths.is_abs_or_var('../a/b/c'))


@istest
def identify_varpath():
    """
    Unit: Paths Identify Variable Path
    Tests that the paths module can successfully identify a path which
    starts with a variable.
    """
    ok_(paths.is_abs_or_var('$a'))
    ok_(paths.is_abs_or_var('$USER/a/b/c'))

    ok_(paths.is_abs_or_var('$a/b/c'))

    ok_(not paths.is_abs_or_var('$$a/b/c'))
    ok_(not paths.is_abs_or_var('$$$$a/b/c'))
    ok_(paths.is_abs_or_var('$$$a/b/c'))
