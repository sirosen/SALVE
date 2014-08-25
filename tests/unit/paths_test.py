#!/usr/bin/python

import mock
from nose.tools import istest

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
        assert paths.get_default_config() == \
               '/tmp/salve/default_settings.ini'


@istest
def identify_abspath():
    """
    Unit: Paths Identify Absolute Path
    Tests that the paths module can successfully identify an absolute
    path as such.
    """
    assert paths.is_abs_or_var('/a')
    assert paths.is_abs_or_var('/a/b/c')
    assert paths.is_abs_or_var('/../a/b/c')

    assert not paths.is_abs_or_var('a')
    assert not paths.is_abs_or_var('a/b/c')
    assert not paths.is_abs_or_var('../a/b/c')


@istest
def identify_varpath():
    """
    Unit: Paths Identify Variable Path
    Tests that the paths module can successfully identify a path which
    starts with a variable.
    """
    assert paths.is_abs_or_var('$a')
    assert paths.is_abs_or_var('$USER/a/b/c')
    assert paths.is_abs_or_var('$a/b/c')

    assert not paths.is_abs_or_var('$$a/b/c')
    assert not paths.is_abs_or_var('$$$$a/b/c')
    assert paths.is_abs_or_var('$$$a/b/c')
