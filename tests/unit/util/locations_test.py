#!/usr/bin/python

import mock
from nose.tools import istest

import src.util.locations


@istest
def get_salve_root():
    """
    Locations Util Get SALVE Root Dir
    Tests the path searching code for the SALVE root.
    This is always relative to locations' __file__ attribute.
    """
    with mock.patch('src.util.locations.__file__',
                    '/tmp/SALVE/src/util/locations.py'):
        assert src.util.locations.get_salve_root() == '/tmp/SALVE'


@istest
def get_default_config():
    """
    Locations Util Get Default Config File
    Tests finding the settings ini file.
    This is, like the SALVE root, always relative to locations.__file__
    """
    with mock.patch('src.util.locations.__file__',
                    '/tmp/SALVE/src/util/locations.py'):
        assert src.util.locations.get_default_config() == \
               '/tmp/SALVE/default_settings.ini'


@istest
def identify_abspath():
    """
    Unit: Locations Util, Identify Absolute Path
    Tests that the locations module can successfully identify an absolute
    path as such.
    """
    assert src.util.locations.is_abs_or_var('/a')
    assert src.util.locations.is_abs_or_var('/a/b/c')
    assert src.util.locations.is_abs_or_var('/../a/b/c')

    assert not src.util.locations.is_abs_or_var('a')
    assert not src.util.locations.is_abs_or_var('a/b/c')
    assert not src.util.locations.is_abs_or_var('../a/b/c')


@istest
def identify_varpath():
    """
    Unit: Locations Util, Identify Variable Path
    Tests that the locations module can successfully identify a path which
    starts with a variable.
    """
    assert src.util.locations.is_abs_or_var('$a')
    assert src.util.locations.is_abs_or_var('$USER/a/b/c')
    assert src.util.locations.is_abs_or_var('$a/b/c')

    assert not src.util.locations.is_abs_or_var('$$a/b/c')
    assert not src.util.locations.is_abs_or_var('$$$$a/b/c')
    assert src.util.locations.is_abs_or_var('$$$a/b/c')
