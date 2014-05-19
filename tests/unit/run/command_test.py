#!/usr/bin/python

import mock
from nose.tools import istest

import src.run.command as command


@istest
def run_on_backup_subcommand():
    """
    Run With Backup Subcommand
    Verifies that running on arguments starting with "backup" correctly invokes
    the backup main method.
    """
    fake_argv = ['./salve.py', 'backup', '-f', 'a/b/c', '-r']

    log = {'main': False}

    def fake_main(args):
        log['main'] = True

    with mock.patch('sys.argv', fake_argv), \
         mock.patch('src.run.backup.main', fake_main):
        command.run()

    assert log['main']
