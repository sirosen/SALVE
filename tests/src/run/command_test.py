#!/usr/bin/python

from nose.tools import istest
from mock import patch, Mock
from tests.utils.exceptions import ensure_except

import src.run.command as command

@istest
def no_manifest_error():
    mock_options = Mock()
    mock_options.manifest = None
    mock_options.gitrepo = None
    def mock_parse():
        return (mock_options,Mock())
    optparser = Mock()
    optparser.parse_args = mock_parse
    def mock_get_optparser():
        return optparser

    # Patch this function to make sure the typical works
    with patch('src.run.command.get_option_parser',mock_get_optparser):
        ensure_except(KeyError,command.read_commandline)

    # Try this with an explicit optparser, should be the same as above
    ensure_except(KeyError,command.read_commandline,optparser)
