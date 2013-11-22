#!/usr/bin/python

import src.util.locations
from nose.tools import istest
from mock import patch

@istest
def get_salve_root():
    with patch('src.util.locations.__file__',
               '/tmp/SALVE/src/util/locations.py'):
        assert src.util.locations.get_salve_root() == '/tmp/SALVE'

@istest
def get_default_config():
    with patch('src.util.locations.__file__',
               '/tmp/SALVE/src/util/locations.py'):
        assert src.util.locations.get_default_config() == \
               '/tmp/SALVE/default_settings.ini'
