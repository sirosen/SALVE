#!/usr/bin/python

import lib.util.locations
from nose.tools import istest, eq_
from mock import patch

@istest
def get_salve_root():
    with patch('lib.util.locations.__file__',
               '/tmp/SALVE/lib/util/locations.py'):
        assert lib.util.locations.get_salve_root() == '/tmp/SALVE'

@istest
def get_default_config():
    with patch('lib.util.locations.__file__',
               '/tmp/SALVE/lib/util/locations.py'):
        assert lib.util.locations.get_default_config() == \
               '/tmp/SALVE/default_settings.ini'
