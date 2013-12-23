#!/usr/bin/python

import os
import mock
import StringIO

from nose.tools import istest
from tests.utils.exceptions import ensure_except

import src.run.command

_testfile_dir = os.path.join(os.path.dirname(__file__),'../testfiles')

def get_full_path(filename):
    return os.path.join(_testfile_dir,filename)

def except_from_args(argv):
    stderr = StringIO.StringIO()
    with mock.patch('sys.argv',argv):
        with mock.patch('sys.stderr',stderr):
            e = ensure_except(SystemExit,src.run.command.main)

    return (e,stderr)

@istest
def unclosed_block_fails():
    """
    E2E: Run on File With Unclosed Block Fails

    Not only validates that a SystemExit occurs, but also
    verifies the exit code and message of the raised exception.
    """
    path = get_full_path('unclosed_block.manifest')
    argv = ['./salve.py','-m',path]
    (e,stderr) = except_from_args(argv)

    assert e.code == 1, "incorrect error code: %d" % e.code
    assert stderr.getvalue() ==\
        "Encountered a SALVE Exception of type TokenizationException"+\
        "\n%s, line 4: " % path +\
        "Tokenizer ended in state BLOCK\n", \
        "%s" % stderr.getvalue()

@istest
def missing_open_fails():
    """
    E2E: Run on File With Missing { Fails

    Not only validates that a SystemExit occurs, but also
    verifies the exit code and message of the raised exception.
    """
    path = get_full_path('missing_open.manifest')
    argv = ['./salve.py','-m',path]
    (e,stderr) = except_from_args(argv)

    assert e.code == 1, "incorrect error code: %d" % e.code
    assert stderr.getvalue() ==\
        "Encountered a SALVE Exception of type TokenizationException"+\
        "\n%s, line 5: " % path +\
        "Unexpected token: } Expected BLOCK_START instead.\n", \
        "%s" % stderr.getvalue()

@istest
def double_identifier_fails():
    """
    E2E: Run on File With Double Identifier Fails

    Not only validates that a SystemExit occurs, but also
    verifies the exit code and message of the raised exception.
    """
    path = get_full_path('double_id.manifest')
    argv = ['./salve.py','-m',path]
    (e,stderr) = except_from_args(argv)

    assert e.code == 1, "incorrect error code: %d" % e.code
    assert stderr.getvalue() ==\
        "Encountered a SALVE Exception of type TokenizationException"+\
        "\n%s, line 5: " % path +\
        "Unexpected token: file Expected BLOCK_START instead.\n", \
        "%s" % stderr.getvalue()

@istest
def missing_identifier_fails():
    """
    E2E: Run on File With Missing Identifier Fails

    Not only validates that a SystemExit occurs, but also
    verifies the exit code and message of the raised exception.
    """
    path = get_full_path('missing_id.manifest')
    argv = ['./salve.py','-m',path]
    (e,stderr) = except_from_args(argv)

    assert e.code == 1, "incorrect error code: %d" % e.code
    assert stderr.getvalue() ==\
        "Encountered a SALVE Exception of type TokenizationException"+\
        "\n%s, line 3: " % path +\
        "Unexpected token: { Expected IDENTIFIER instead.\n", \
        "%s" % stderr.getvalue()

@istest
def missing_value_fails():
    """
    E2E: Run on File With Missing Attr Value Fails

    Not only validates that a SystemExit occurs, but also
    verifies the exit code and message of the raised exception.
    """
    path = get_full_path('missing_attr_val.manifest')
    argv = ['./salve.py','-m',path]
    (e,stderr) = except_from_args(argv)

    assert e.code == 1, "incorrect error code: %d" % e.code
    assert stderr.getvalue() ==\
        "Encountered a SALVE Exception of type TokenizationException"+\
        "\n%s, line 5: " % path +\
        "Unexpected token: } Expected TEMPLATE instead.\n", \
        "%s" % stderr.getvalue()

@istest
def double_open_fails():
    """
    E2E: Run on File With Double { Fails

    Not only validates that a SystemExit occurs, but also
    verifies the exit code and message of the raised exception.
    """
    path = get_full_path('double_open.manifest')
    argv = ['./salve.py','-m',path]
    (e,stderr) = except_from_args(argv)

    assert e.code == 1, "incorrect error code: %d" % e.code
    assert stderr.getvalue() ==\
        "Encountered a SALVE Exception of type TokenizationException"+\
        "\n%s, line 3: " % path +\
        "Unexpected token: { Expected ['BLOCK_END', 'IDENTIFIER'] instead.\n", \
        "%s" % stderr.getvalue()

@istest
def invalid_block_id_fails():
    """
    E2E: Run on File With Invalid Block ID Fails

    Not only validates that a SystemExit occurs, but also
    verifies the exit code and message of the raised exception.
    """
    path = get_full_path('invalid_block_id.manifest')
    argv = ['./salve.py','-m',path]
    (e,stderr) = except_from_args(argv)

    assert e.code == 1, "incorrect error code: %d" % e.code
    assert stderr.getvalue() ==\
        "Encountered a SALVE Exception of type ParsingException"+\
        "\n%s, line 7: " % path +\
        "Invalid block id invalid_block_id\n", \
        "%s" % stderr.getvalue()
