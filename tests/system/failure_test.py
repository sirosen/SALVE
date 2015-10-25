import os
import mock

from nose.tools import istest
from tests.util import ensure_except, full_path, assert_substr
from tests import system

from salve import cli


def except_from_args(argv):
    with mock.patch('sys.argv', argv):
        return ensure_except(SystemExit, cli.main)


def except_from_relpath(rpath):
    """Common case in which we just want to run and trigger an exception
    Also passes back some basically processed versions of the path"""
    path = full_path(rpath)
    argv = ['./salve.py', 'deploy', '-m', path]
    return except_from_args(argv), path, os.path.relpath(path, '.')


def assert_exit1(e):
    assert e.code == 1, "incorrect error code: %d" % e.code


class TestWithScratchdir(system.RunScratchContainer):
    def strs_in_stderr(self, path, rpath, strs):
        err = self.stderr.getvalue()
        for expected in strs:
            expected = expected.format(rpath, path)
            assert_substr(err, expected)

    def _check_errors(self, man_path, stderr_strs):
        e, path, rpath = except_from_relpath(man_path)
        self.strs_in_stderr(path, rpath, stderr_strs)
        assert_exit1(e)

    @istest
    def unclosed_block_fails(self):
        """
        System: Run on File With Unclosed Block Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        self._check_errors('unclosed_block.manifest', [
            'PARSING [INFO] Beginning Tokenization of "{1}"',
            "PARSING [ERROR] {0}, line 4: Tokenizer ended in state BLOCK"
        ])

    @istest
    def missing_open_fails(self):
        """
        System: Run on File With Missing { Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        self._check_errors('missing_open.manifest', [
            'PARSING [INFO] Beginning Tokenization of "{1}"',
            ("PARSING [ERROR] {0}, line 5: Unexpected token: }} Expected " +
             "['BLOCK_START', 'TEMPLATE'] instead.")
        ])

    @istest
    def missing_identifier_fails(self):
        """
        System: Run on File With Missing Identifier Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        self._check_errors('missing_id.manifest', [
            'PARSING [INFO] Beginning Tokenization of "{1}"',
            ("PARSING [ERROR] {0}, line 3: Unexpected token: {{ Expected " +
             "IDENTIFIER instead.")
        ])

    @istest
    def missing_value_fails(self):
        """
        System: Run on File With Missing Attr Value Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        self._check_errors('missing_attr_val.manifest', [
            'PARSING [INFO] Beginning Tokenization of "{1}"',
            ("PARSING [ERROR] {0}, line 5: Unexpected token: }} Expected " +
             "TEMPLATE instead.")
        ])

    @istest
    def double_open_fails(self):
        """
        System: Run on File With Double { Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        self._check_errors('double_open.manifest', [
            'PARSING [INFO] Beginning Tokenization of "{1}"',
            ("PARSING [ERROR] {0}, line 3: Unexpected token: {{ Expected " +
             "['BLOCK_END', 'IDENTIFIER'] instead.")
        ])

    @istest
    def invalid_block_id_fails(self):
        """
        System: Run on File With Invalid Block ID Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        self._check_errors('invalid_block_id.manifest', [
            'PARSING [INFO] Beginning Tokenization of "{1}"',
            'PARSING [INFO] Finished Tokenization of "{1}"',
            'PARSING [INFO] Beginning Parse of Token Stream',
            ('PARSING [INFO] {0}, line 3: Generating Block From Identifier ' +
             'Token: Token(value=file,ty=IDENTIFIER,lineno=3,filename={0})'),
            ('PARSING [INFO] {0}, line 7: Generating Block From Identifier ' +
             'Token: Token(value=invalid_block_id,ty=IDENTIFIER,lineno=7,' +
             'filename={0})'),
            ('PARSING [ERROR] {0}, line 7: Invalid block id invalid_block_id')
        ])
