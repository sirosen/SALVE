#!/usr/bin/python

import os
import mock

from nose.tools import istest
from tests.util import ensure_except, full_path
from tests import system

from salve import cli


def except_from_args(argv):
    with mock.patch('sys.argv', argv):
        e = ensure_except(SystemExit, cli.main)

    return e


parsing_transition_debug_string = (
    "[DEBUG] SALVE Execution Phase Transition [STARTUP] -> [PARSING]")


class TestWithScratchdir(system.RunScratchContainer):
    @istest
    def unclosed_block_fails(self):
        """
        System: Run on File With Unclosed Block Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        path = full_path('unclosed_block.manifest')
        rpath = os.path.relpath(path, '.')
        argv = ['./salve.py', 'deploy', '-m', path]
        e = except_from_args(argv)

        expected_stderr = '\n'.join((
            parsing_transition_debug_string,
            'PARSING [INFO] Beginning Tokenization of "%s"' % path,
            ("PARSING [ERROR] %s, line 4: " % rpath +
             "Tokenizer ended in state BLOCK\n")
            ))
        assert self.stderr.getvalue() == expected_stderr, \
            self.stderr.getvalue()
        assert e.code == 1, "incorrect error code: %d" % e.code

    @istest
    def missing_open_fails(self):
        """
        System: Run on File With Missing { Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        path = full_path('missing_open.manifest')
        rpath = os.path.relpath(path, '.')
        argv = ['./salve.py', 'deploy', '-m', path]
        e = except_from_args(argv)

        expected_stderr = '\n'.join((
            parsing_transition_debug_string,
            'PARSING [INFO] Beginning Tokenization of "%s"' % path,
            ("PARSING [ERROR] %s, line 5: " % rpath +
             "Unexpected token: } Expected " +
             "['BLOCK_START', 'TEMPLATE'] instead.\n")
            ))
        assert self.stderr.getvalue() == expected_stderr, \
            self.stderr.getvalue()
        assert e.code == 1, "incorrect error code: %d" % e.code

    @istest
    def missing_identifier_fails(self):
        """
        System: Run on File With Missing Identifier Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        path = full_path('missing_id.manifest')
        rpath = os.path.relpath(path, '.')
        argv = ['./salve.py', 'deploy', '-m', path]
        e = except_from_args(argv)

        expected_stderr = '\n'.join((
            parsing_transition_debug_string,
            'PARSING [INFO] Beginning Tokenization of "%s"' % path,
            ("PARSING [ERROR] %s, line 3: " % rpath +
             "Unexpected token: { Expected IDENTIFIER instead.\n")
            ))
        assert self.stderr.getvalue() == expected_stderr, \
            self.stderr.getvalue()
        assert e.code == 1, "incorrect error code: %d" % e.code

    @istest
    def missing_value_fails(self):
        """
        System: Run on File With Missing Attr Value Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        path = full_path('missing_attr_val.manifest')
        rpath = os.path.relpath(path, '.')
        argv = ['./salve.py', 'deploy', '-m', path]
        e = except_from_args(argv)

        expected_stderr = '\n'.join((
            parsing_transition_debug_string,
            'PARSING [INFO] Beginning Tokenization of "%s"' % path,
            ('PARSING [ERROR] %s, line 5: ' % rpath +
             'Unexpected token: } Expected TEMPLATE instead.\n')
            ))
        assert self.stderr.getvalue() == expected_stderr, \
            self.stderr.getvalue()
        assert e.code == 1, "incorrect error code: %d" % e.code

    @istest
    def double_open_fails(self):
        """
        System: Run on File With Double { Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        path = full_path('double_open.manifest')
        rpath = os.path.relpath(path, '.')
        argv = ['./salve.py', 'deploy', '-m', path]
        e = except_from_args(argv)

        expected_stderr = '\n'.join((
            parsing_transition_debug_string,
            'PARSING [INFO] Beginning Tokenization of "%s"' % path,
            ("PARSING [ERROR] %s, line 3: " % rpath +
             "Unexpected token: { Expected ['BLOCK_END', 'IDENTIFIER'] " +
             "instead.\n")
            ))
        assert self.stderr.getvalue() == expected_stderr, \
            self.stderr.getvalue()
        assert e.code == 1, "incorrect error code: %d" % e.code

    @istest
    def invalid_block_id_fails(self):
        """
        System: Run on File With Invalid Block ID Fails

        Not only validates that a SystemExit occurs, but also
        verifies the exit code and message of the raised exception.
        """
        path = full_path('invalid_block_id.manifest')
        rpath = os.path.relpath(path, '.')
        argv = ['./salve.py', 'deploy', '-m', path]
        e = except_from_args(argv)

        expected_stderr = '\n'.join((
            parsing_transition_debug_string,
            'PARSING [INFO] Beginning Tokenization of "%s"' % path,
            'PARSING [INFO] Finished Tokenization of "%s"' % path,
            'PARSING [INFO] Beginning Parse of Token Stream',
            ('PARSING [INFO] {0}, line 3: ' +
             'Generating Block From Identifier Token: ' +
             'Token(value=file,ty=IDENTIFIER,lineno=3,filename={0})'
             ).format(rpath),
            ('PARSING [INFO] {0}, line 7: ' +
             'Generating Block From Identifier Token: ' +
             'Token(value=invalid_block_id,ty=IDENTIFIER,' +
             'lineno=7,filename={0})'
             ).format(rpath),
            ("PARSING [ERROR] %s, line 7: " % rpath +
             "Invalid block id invalid_block_id\n")
            ))
        assert self.stderr.getvalue() == expected_stderr, \
            self.stderr.getvalue()
        assert e.code == 1, "incorrect error code: %d" % e.code
