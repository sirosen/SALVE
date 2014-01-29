#!/usr/bin/python

import os
import mock
import shlex
from nose.tools import istest

import tests.end2end.run.common as run_common

class TestWithScratchdir(run_common.RunScratchContainer):
    @istest
    def copy_single_file(self):
        """
        E2E: Copy a Single File

        Runs a manifest which copies itself and verifies the contents of
        the destination file.
        """
        content = 'file { action copy source 1.man target 2.man }\n'
        self.write_file('1.man',content)
        self.run_on_manifest('1.man')
        assert self.exists('2.man')
        s = self.read_file('2.man')
        assert s == content, '%s' % s

    @istest
    def implicit_copy_single_file(self):
        """
        E2E: Implicit Copy a Single File

        Runs a manifest which copies itself and verifies the contents of
        the destination file.
        """
        content = 'file { source 1.man target 2.man }\n'
        self.write_file('1.man',content)
        self.run_on_manifest('1.man')
        assert self.exists('2.man')
        s = self.read_file('2.man')
        assert s == content, '%s' % s

    @istest
    def copy_two_files(self):
        """
        E2E: Copy Two Files

        Runs a manifest which copies two files and verifies the contents of
        the destination files.
        """
        self.write_file('1.man',
            'file { action copy source f1 target f1prime }\n'+\
            'file { source f2 target f2prime }\n'
            )
        f1_content = 'alpha beta\n'
        f2_content = 'gamma\ndelta\n'
        self.write_file('f1',f1_content)
        self.write_file('f2',f2_content)

        self.run_on_manifest('1.man')

        assert self.exists('f1prime')
        assert self.exists('f2prime')
        s = self.read_file('f1prime')
        assert s == f1_content, '%s' % s
        s = self.read_file('f2prime')
        assert s == f2_content, '%s' % s

    @istest
    def create_single_file(self):
        """
        E2E: Create a Single File

        Runs a manifest which creates a file and verifies the contents of
        the destination file are nil.
        """
        content = 'file { action create target f2 }\n'
        self.write_file('1.man',content)
        self.run_on_manifest('1.man')
        assert self.exists('f2')
        s = self.read_file('f2')
        assert s == '', '%s' % s

    @istest
    def create_multiple_files(self):
        """
        E2E: Create Multiple Files

        Runs a manifest which creates two files and verifies the contents of
        the destination file are nil.
        """
        content = 'file{action create target f2}\nfile{action\ncreate target f3}'
        self.write_file('1.man',content)
        self.run_on_manifest('1.man')
        assert self.exists('f2')
        assert self.exists('f3')
        s = self.read_file('f2')
        assert s == '', '%s' % s
        s = self.read_file('f3')
        assert s == '', '%s' % s

    @istest
    def create_existing_file(self):
        """
        E2E: Create Existing File

        Runs a manifest which touches an existing file and verifies the
        contents of the destination file do not change.
        """
        content = 'file{action create target f1}\n'
        self.write_file('1.man',content)
        f1_content = 'alpha beta\n'
        self.write_file('f1',f1_content)
        self.run_on_manifest('1.man')
        assert self.exists('f1')
        s = self.read_file('f1')
        assert s == f1_content, '%s' % s

    @istest
    def change_file_permissions(self):
        """
        E2E: Change Single File Permissions

        Runs a manifest which touches several files and verifies the
        permissions of the target files.
        """
        content = 'file{action create target f1 mode 444}\n'
        self.write_file('1.man',content)
        self.run_on_manifest('1.man')
        assert self.exists('f1')
        s = self.read_file('f1')
        assert s == '', '%s' % s
        assert self.get_mode('f1') == int('444',8)

    @istest
    def change_own_permissions(self):
        """
        E2E: Reflexive Manifest Permissions Change

        Runs a manifest which changes its own permissions to remove user
        read/write permissions.
        """
        content = 'file{action create target 1.man mode 066}\n'
        self.write_file('1.man',content)
        self.run_on_manifest('1.man')
        assert self.exists('1.man')
        assert self.get_mode('1.man') == int('066',8)

    @istest
    def copy_file_triggers_backup(self):
        """
        E2E: Copy File Triggers Backup

        Runs a manifest which copies itself and verifies the contents of
        the destination file.
        """
        backup_dir = 'home/user1/backups'
        backup_log = 'home/user1/backup.log'
        self.make_dir(backup_dir)
        self.write_file(backup_log,'')
        self.write_file('f1','')

        content = 'file { action copy source 1.man target f1 }\n'

        self.write_file('1.man',content)
        self.run_on_manifest('1.man')

        s = self.read_file('f1')
        assert s == content, '%s' % s
        s = self.read_file(backup_log).strip()
        ss = shlex.split(s)
        assert len(ss) == 4
        assert ss[3] == self.get_fullname('f1')
        backup_path = self.get_backup_path(backup_dir)
        backup_path = os.path.join(backup_path,ss[2])
        s = self.read_file(backup_path)
        assert s == ''

    @istest
    def copy_file_triggers_backup_implicit_dir(self):
        """
        E2E: Copy File Implicit Backup Dir

        Runs a manifest which copies itself and verifies the contents of
        the destination file.
        """
        backup_dir = 'home/user1/backups'
        backup_log = 'home/user1/backup.log'
        self.write_file('f1','')

        content = 'file { action copy source 1.man target f1 }\n'

        self.write_file('1.man',content)
        self.run_on_manifest('1.man')

        s = self.read_file('f1')
        assert s == content, '%s' % s
        s = self.read_file(backup_log).strip()
        ss = shlex.split(s)
        assert len(ss) == 4
        assert ss[3] == self.get_fullname('f1')
        backup_path = self.get_backup_path(backup_dir)
        backup_path = os.path.join(backup_path,ss[2])
        s = self.read_file(backup_path)
        assert s == ''
