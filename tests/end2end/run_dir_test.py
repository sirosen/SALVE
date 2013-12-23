#!/usr/bin/python

import os
import mock
from nose.tools import istest, with_setup

import src.run.command
import tests.utils.scratch

def run_on_args(argv):
    with mock.patch('sys.argv',argv):
        return src.run.command.main()

class TestWithScratchdir(tests.utils.scratch.ScratchContainer):
    @istest
    def copy_empty_dir(self):
        """
        E2E: Copy an Empty Directory

        Runs a manifest which copies an empty directory. Verifies that
        the target is created, and that it is empty as well.
        """
        self.make_dir('a')
        content = 'directory { action copy source a target b }\n'
        self.write_file('1.man',content)
        man_path = self.get_fullname('1.man')
        run_on_args(['./salve.py','-m',man_path])

        assert self.exists('b')
        # make sure the original is unharmed
        assert self.exists('a')
        assert len(self.listdir('b')) == 0

    @istest
    def implicit_copy_action(self):
        """
        E2E: Copy Directory Implicit Action

        Runs a manifest which copies an empty directory. Verifies that
        the target is created, and that it is empty as well.
        """
        self.make_dir('a')
        content = 'directory { source a target b }\n'
        self.write_file('1.man',content)
        man_path = self.get_fullname('1.man')
        run_on_args(['./salve.py','-m',man_path])

        assert self.exists('b')
        # make sure the original is unharmed
        assert self.exists('a')
        assert len(self.listdir('b')) == 0

    @istest
    def create_dir(self):
        """
        E2E: Create a Directory

        Runs a manifest which copies an empty directory. Verifies that
        the target is created, and that it is empty as well.
        """
        content = 'directory { action create target a }\n'
        self.write_file('1.man',content)
        man_path = self.get_fullname('1.man')
        run_on_args(['./salve.py','-m',man_path])

        assert self.exists('a')
        assert len(self.listdir('a')) == 0

    @istest
    def set_dir_mode(self):
        """
        E2E: Create a Directory to Set Mode

        Runs a manifest which copies an empty directory. Verifies that
        the target is created, and that it is empty as well.
        """
        self.make_dir('a')
        content = 'directory { action create target a mode 700 }\n'
        self.write_file('1.man',content)
        man_path = self.get_fullname('1.man')
        run_on_args(['./salve.py','-m',man_path])

        assert self.exists('a')
        assert len(self.listdir('a')) == 0
        assert self.get_mode('a') == int('700',8)

    @istest
    def copy_dir_with_file(self):
        """
        E2E: Copy Directory With File

        Runs a manifest which copies an directory containing one file.
        Verifies that the target is created, and that it has a duplicate
        of that file.
        """
        self.make_dir('p')
        content = 'directory { action copy source p target q }\n'
        self.write_file('1.man',content)
        self.write_file('p/alpha','string here!')
        man_path = self.get_fullname('1.man')
        run_on_args(['./salve.py','-m',man_path])

        assert self.exists('q')
        # make sure the original is unharmed
        assert self.exists('p')

        ls_result = self.listdir('q')
        assert len(ls_result) == 1
        assert ls_result[0] == 'alpha'
        s = self.read_file('q/alpha').strip()
        assert s == 'string here!'

    @istest
    def copy_dir_containing_empty_dir(self):
        """
        E2E: Copy Directory Containing Empty Directory

        Runs a manifest which copies an directory containing an empty dir.
        Verifies that the target is created, and that it has a duplicate
        of the original dir contents.
        """
        self.make_dir('m/n')
        content = 'directory { action copy source m target m_prime }\n'
        self.write_file('manifest',content)
        man_path = self.get_fullname('manifest')
        run_on_args(['./salve.py','-m',man_path])

        assert self.exists('m_prime')
        # make sure the original is unharmed
        assert self.exists('m')
        assert self.exists('m/n')

        ls_result = self.listdir('m_prime')
        assert len(ls_result) == 1
        assert ls_result[0] == 'n'
        ls_result = self.listdir('m_prime/n')
        assert len(ls_result) == 0

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
        self.write_file('manifest',content)
        self.write_file('a/f1',af1_content)
        self.write_file('b/f1',bf1_content)

        man_path = self.get_fullname('manifest')
        run_on_args(['./salve.py','-m',man_path])

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
        backup = self.get_backup_path('home/user1/backups','b/f1')
        assert self.exists(backup)
        backup_files = self.listdir(backup)
        assert len(backup_files) == 1
        backup_file = os.path.join(backup,backup_files[0])
        s = self.read_file(backup_file).strip()
        assert s == 'old'
