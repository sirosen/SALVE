#!/usr/bin/python

import os
import mock

from nose.tools import istest
from tests.utils.exceptions import ensure_except
import tests.end2end.run.common as run_common

import salve.run.command

_testfile_dir = os.path.join(os.path.dirname(__file__), '../testfiles')


def get_full_path(filename):
    return os.path.join(_testfile_dir, filename)


def except_from_args(argv):
    with mock.patch('sys.argv', argv):
        e = ensure_except(SystemExit, salve.run.command.run)

    return e


class TestWithScratchdir(run_common.RunScratchContainer):
    @istest
    def unclosed_block_fails(self):
        """
        E2E: Run on File With Unclosed Block Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        path = get_full_path('unclosed_block.manifest')
        rpath = os.path.relpath(path, '.')
        argv = ['./salve.py', 'deploy', '-m', path]
        e = except_from_args(argv)

        assert self.stderr.getvalue() ==\
            "[ERROR] [PARSING] %s, line 4: " % rpath +\
            "Tokenizer ended in state BLOCK\n", \
            self.stderr.getvalue()
        assert e.code == 1, "incorrect error code: %d" % e.code

    @istest
    def missing_open_fails(self):
        """
        E2E: Run on File With Missing { Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        path = get_full_path('missing_open.manifest')
        rpath = os.path.relpath(path, '.')
        argv = ['./salve.py', 'deploy', '-m', path]
        e = except_from_args(argv)

        assert self.stderr.getvalue() ==\
            "[ERROR] [PARSING] %s, line 5: " % rpath +\
            "Unexpected token: } Expected BLOCK_START instead.\n", \
            self.stderr.getvalue()
        assert e.code == 1, "incorrect error code: %d" % e.code

    @istest
    def double_identifier_fails(self):
        """
        E2E: Run on File With Double Identifier Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        path = get_full_path('double_id.manifest')
        rpath = os.path.relpath(path, '.')
        argv = ['./salve.py', 'deploy', '-m', path]
        e = except_from_args(argv)

        assert self.stderr.getvalue() ==\
            "[ERROR] [PARSING] %s, line 5: " % rpath +\
            "Unexpected token: file Expected BLOCK_START instead.\n", \
            self.stderr.getvalue()
        assert e.code == 1, "incorrect error code: %d" % e.code

    @istest
    def missing_identifier_fails(self):
        """
        E2E: Run on File With Missing Identifier Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        path = get_full_path('missing_id.manifest')
        rpath = os.path.relpath(path, '.')
        argv = ['./salve.py', 'deploy', '-m', path]
        e = except_from_args(argv)

        assert self.stderr.getvalue() ==\
            "[ERROR] [PARSING] %s, line 3: " % rpath +\
            "Unexpected token: { Expected IDENTIFIER instead.\n", \
            self.stderr.getvalue()
        assert e.code == 1, "incorrect error code: %d" % e.code

    @istest
    def missing_value_fails(self):
        """
        E2E: Run on File With Missing Attr Value Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        path = get_full_path('missing_attr_val.manifest')
        rpath = os.path.relpath(path, '.')
        argv = ['./salve.py', 'deploy', '-m', path]
        e = except_from_args(argv)

        assert self.stderr.getvalue() ==\
            "[ERROR] [PARSING] %s, line 5: " % rpath +\
            "Unexpected token: } Expected TEMPLATE instead.\n", \
            self.stderr.getvalue()
        assert e.code == 1, "incorrect error code: %d" % e.code

    @istest
    def double_open_fails(self):
        """
        E2E: Run on File With Double { Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        path = get_full_path('double_open.manifest')
        rpath = os.path.relpath(path, '.')
        argv = ['./salve.py', 'deploy', '-m', path]
        e = except_from_args(argv)

        assert (self.stderr.getvalue() ==
            ("[ERROR] [PARSING] %s, line 3: " % rpath +
            "Unexpected token: { Expected ['BLOCK_END', 'IDENTIFIER'] " +
            "instead.\n")), self.stderr.getvalue()
        assert e.code == 1, "incorrect error code: %d" % e.code

    @istest
    def invalid_block_id_fails(self):
        """
        E2E: Run on File With Invalid Block ID Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        path = get_full_path('invalid_block_id.manifest')
        rpath = os.path.relpath(path, '.')
        argv = ['./salve.py', 'deploy', '-m', path]
        e = except_from_args(argv)

        assert self.stderr.getvalue() ==\
            "[ERROR] [PARSING] %s, line 7: " % rpath +\
            "Invalid block id invalid_block_id\n", \
            self.stderr.getvalue()
        assert e.code == 1, "incorrect error code: %d" % e.code
