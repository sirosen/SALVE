#!/usr/bin/python

import os
import shlex
from nose.tools import istest

from tests.end2end.cli import common


class TestWithScratchdir(common.RunScratchContainer):
    @istest
    def copy_file_triggers_backup(self):
        """
        E2E: Copy File Triggers Backup

        Runs a manifest which copies itself and verifies the contents of
        the destination file.
        """
        backup_dir = 'home/user1/backups'
        backup_log = 'home/user1/backup.log'
        self.make_dir(os.path.join(backup_dir, 'files'))
        self.write_file(backup_log, '')
        self.write_file('f1', '')

        content = 'file { action copy source 1.man target f1 }\n'

        self.write_file('1.man', content)
        self.run_on_manifest('1.man')

        s = self.read_file('f1')
        assert s == content, '%s' % s
        s = self.read_file(backup_log).strip()
        ss = shlex.split(s)
        assert len(ss) == 4
        assert ss[3] == self.get_fullname('f1')
        backup_path = self.get_backup_path(backup_dir)
        backup_path = os.path.join(backup_path, ss[2])
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
        self.write_file('f1', '')

        content = 'file { action copy source 1.man target f1 }\n'

        self.write_file('1.man', content)
        self.run_on_manifest('1.man')

        s = self.read_file('f1')
        assert s == content, '%s' % s
        s = self.read_file(backup_log).strip()
        ss = shlex.split(s)
        assert len(ss) == 4
        assert ss[3] == self.get_fullname('f1')
        backup_path = self.get_backup_path(backup_dir)
        backup_path = os.path.join(backup_path, ss[2])
        s = self.read_file(backup_path)
        assert s == ''

    @istest
    def copy_dir_triggers_backup(self):
        """
        E2E: Copy Directory Triggers File Backup

        Runs a manifest which copies an directory containing an empty dir.
        Verifies that the target is created, and that it has a duplicate
        of the original dir contents.
        """
        self.make_dir('a')
        self.make_dir('b')
        content = 'directory { action copy source a target b }\n'
        af1_content = 'new'
        bf1_content = 'old'
        self.write_file('manifest', content)
        self.write_file('a/f1', af1_content)
        self.write_file('b/f1', bf1_content)

        self.run_on_manifest('manifest')

        backup_dir = 'home/user1/backups'
        backup_log = 'home/usr1/backup.log'

        assert self.exists('b')
        assert self.exists('b/f1')
        s = self.read_file('b/f1').strip()
        assert s == 'new'
        # make sure the original is unharmed
        assert self.exists('a')
        assert self.exists('a/f1')
        s = self.read_file('a/f1').strip()
        assert s == 'new'

        assert self.exists('home/user1/backup.log')
        assert self.exists('home/user1/backups')
        backup = self.get_backup_path('home/user1/backups')
        assert self.exists(backup)
        backup_files = self.listdir(backup)
        assert len(backup_files) == 1
        backup_file = os.path.join(backup, backup_files[0])
        s = self.read_file(backup_file).strip()
        assert s == 'old'

    @istest
    def unwritable_backupdir_cancel(self):
        """
        E2E: Unwritable Backup Dir Cancels Backup

        Runs a file copy to trigger a backup with an unwritable backup dir.
        Verifies that no backup action takes place.
        """
        backup_dir = 'home/user1/backups'
        backup_log = 'home/user1/backup.log'
        self.write_file(backup_log, '')
        self.write_file('f1', '')

        # set mode to not include write privileges
        backup_path = self.get_backup_path(backup_dir)
        self.make_dir(backup_path)
        os.chmod(backup_path, int('500', 8))

        content = 'file { action copy source 1.man target f1 }\n'

        self.write_file('1.man', content)
        self.run_on_manifest('1.man')

        s = self.read_file('f1')
        assert s == content, '%s' % s
        s = self.read_file(backup_log).strip()
        assert s == ''
        assert len(os.listdir(backup_path)) == 0
        os.chmod(backup_path, int('700', 8))

    @istest
    def unwritable_backupdir_cancel(self):
        """
        E2E: Unwritable Backup Parent Dir Cancels Backup

        Runs a file copy to trigger a backup with an unwritable backup parent
        dir. Verifies that no backup action takes place.
        """
        backup_dir = 'home/user1/backups'
        backup_log = 'home/user1/backup.log'
        self.write_file(backup_log, '')
        self.write_file('f1', '')

        self.make_dir(backup_dir)
        backup_dir_full = self.get_fullname(backup_dir)
        os.chmod(backup_dir_full, int('500', 8))

        content = 'file { action copy source 1.man target f1 }\n'

        self.write_file('1.man', content)
        self.run_on_manifest('1.man')

        s = self.read_file('f1')
        assert s == content, '%s' % s
        s = self.read_file(backup_log).strip()
        assert s == ''
        assert len(os.listdir(backup_dir_full)) == 0

        os.chmod(backup_dir_full, int('700', 8))

    @istest
    def unreadable_source_cancel(self):
        """
        E2E: Unreadable Source File Cancels Backup

        Verifies that if the source file is not readable, the bakcup action
        will be cancelled.
        """
        backup_dir = 'home/user1/backups'
        backup_log = 'home/user1/backup.log'
        self.write_file(backup_log, '')
        self.write_file('f1', '')

        backup_path = self.get_backup_path(backup_dir)
        self.make_dir(backup_path)
        fullname = self.get_fullname('f1')
        os.chmod(fullname, int('300', 8))

        content = 'file { action copy source 1.man target f1 }\n'

        self.write_file('1.man', content)
        self.run_on_manifest('1.man')

        os.chmod(fullname, int('700', 8))

        s = self.read_file('f1')
        assert s == content, '%s' % s

        s = self.read_file(backup_log).strip()
        assert s == ''
        assert len(os.listdir(backup_path)) == 0
