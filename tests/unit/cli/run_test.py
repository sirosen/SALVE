#!/usr/bin/python

import mock
from nose.tools import istest

from salve import cli


@istest
def run_on_backup_subcommand():
    """
    Unit: Run With Backup Subcommand
    Verifies that running on arguments starting with "backup" correctly invokes
    the backup main method.
    """
    fake_argv = ['./salve.py', 'backup', '-f', 'a/b/c', '-r']

    log = {'main': False}

    def fake_main(args):
        log['main'] = True

    with mock.patch('sys.argv', fake_argv):
        with mock.patch('salve.cli.backup.main', fake_main):
            cli.run()

    assert log['main']
