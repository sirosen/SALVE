#!/usr/bin/python

import mock
from nose.tools import istest

import salve.util.locations


@istest
def get_default_config():
    """
    Unit: Locations Util Get Default Config File
    Tests finding the settings ini file.
    This is, like the SALVE root, always relative to locations.__file__
    """
    with mock.patch('salve.util.locations.__file__',
                    '/tmp/salve/util/locations.py'):
        assert salve.util.locations.get_default_config() == \
               '/tmp/salve/default_settings.ini'


@istest
def identify_abspath():
    """
    Unit: Locations Util, Identify Absolute Path
    Tests that the locations module can successfully identify an absolute
    path as such.
    """
    assert salve.util.locations.is_abs_or_var('/a')
    assert salve.util.locations.is_abs_or_var('/a/b/c')
    assert salve.util.locations.is_abs_or_var('/../a/b/c')

    assert not salve.util.locations.is_abs_or_var('a')
    assert not salve.util.locations.is_abs_or_var('a/b/c')
    assert not salve.util.locations.is_abs_or_var('../a/b/c')


@istest
def identify_varpath():
    """
    Unit: Locations Util, Identify Variable Path
    Tests that the locations module can successfully identify a path which
    starts with a variable.
    """
    assert salve.util.locations.is_abs_or_var('$a')
    assert salve.util.locations.is_abs_or_var('$USER/a/b/c')
    assert salve.util.locations.is_abs_or_var('$a/b/c')

    assert not salve.util.locations.is_abs_or_var('$$a/b/c')
    assert not salve.util.locations.is_abs_or_var('$$$$a/b/c')
    assert salve.util.locations.is_abs_or_var('$$$a/b/c')
