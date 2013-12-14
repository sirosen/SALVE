#!/usr/bin/python

from nose.tools import istest, with_setup
import mock, os, shlex

import src.run.command
import tests.utils.scratch

def run_on_args(argv):
    with mock.patch('sys.argv',argv):
        return src.run.command.main()

class TestWithScratchdir(tests.utils.scratch.ScratchContainer):
    @istest
    def copy_single_file(self):
        """
        E2E: Copy a Single File

        Runs a manifest which copies itself and verifies the contents of
        the destination file.
        """
        cwd = self.scratch_dir
        content = 'file { action copy source 1.man target 2.man }\n'
        self.write_file('1.man',content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])
        assert os.path.exists(os.path.join(cwd,'2.man'))
        s = self.read_file('2.man')
        assert s == content, '%s' % s

    @istest
    def implicit_copy_single_file(self):
        """
        E2E: Implicit Copy a Single File

        Runs a manifest which copies itself and verifies the contents of
        the destination file.
        """
        cwd = self.scratch_dir
        content = 'file { source 1.man target 2.man }\n'
        self.write_file('1.man',content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])
        assert os.path.exists(os.path.join(cwd,'2.man'))
        s = self.read_file('2.man')
        assert s == content, '%s' % s

    @istest
    def copy_two_files(self):
        """
        E2E: Copy Two Files

        Runs a manifest which copies two files and verifies the contents of
        the destination files.
        """
        cwd = self.scratch_dir
        man_path = os.path.join(cwd,'1.man')
        self.write_file('1.man',
            'file { action copy source f1 target f1prime }\n'+\
            'file { source f2 target f2prime }\n'
            )
        f1_content = 'alpha beta\n'
        f2_content = 'gamma\ndelta\n'
        self.write_file('f1',f1_content)
        self.write_file('f2',f2_content)

        run_on_args(['./salve.py','-m',man_path])

        assert os.path.exists(os.path.join(cwd,'f1prime'))
        assert os.path.exists(os.path.join(cwd,'f2prime'))
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
        cwd = self.scratch_dir
        content = 'file { action create target f2 }\n'
        self.write_file('1.man',content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])
        assert os.path.exists(os.path.join(cwd,'f2'))
        s = self.read_file('f2')
        assert s == '', '%s' % s

    @istest
    def create_multiple_files(self):
        """
        E2E: Create Multiple Files

        Runs a manifest which creates two files and verifies the contents of
        the destination file are nil.
        """
        cwd = self.scratch_dir
        content = 'file{action create target f2}\nfile{action\ncreate target f3}'
        self.write_file('1.man',content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])
        assert os.path.exists(os.path.join(cwd,'f2'))
        assert os.path.exists(os.path.join(cwd,'f3'))
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
        cwd = self.scratch_dir
        content = 'file{action create target f1}\n'
        self.write_file('1.man',content)
        f1_content = 'alpha beta\n'
        self.write_file('f1',f1_content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])
        assert os.path.exists(os.path.join(cwd,'f1'))
        s = self.read_file('f1')
        assert s == f1_content, '%s' % s

    @istest
    def change_file_permissions(self):
        """
        E2E: Change Single File Permissions

        Runs a manifest which touches several files and verifies the
        permissions of the target files.
        """
        cwd = self.scratch_dir
        content = 'file{action create target f1 mode 444}\n'
        self.write_file('1.man',content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])
        assert os.path.exists(os.path.join(cwd,'f1'))
        s = self.read_file('f1')
        assert s == '', '%s' % s
        assert self.get_file_mode('f1') == int('444',8)

    @istest
    def change_own_permissions(self):
        """
        E2E: Reflexive Manifest Permissions Change

        Runs a manifest which changes its own permissions to remove user
        read/write permissions.
        """
        cwd = self.scratch_dir
        content = 'file{action create target 1.man mode 066}\n'
        self.write_file('1.man',content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])
        assert os.path.exists(os.path.join(cwd,'1.man'))
        assert self.get_file_mode('1.man') == int('066',8)

    @istest
    def copy_file_triggers_backup(self):
        """
        E2E: Copy a Single File

        Runs a manifest which copies itself and verifies the contents of
        the destination file.
        """
        cwd = self.scratch_dir
        backup_dir = 'backups'
        backup_log = 'backup.log'
        self.make_dir(backup_dir)
        self.write_file(backup_log,'')
        self.write_file('f1','')

        content = 'file { action copy source 1.man target f1 '+\
                  'backup_dir %s ' % backup_dir +\
                  'backup_log %s ' % backup_log + '}\n'

        self.write_file('1.man',content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])

        s = self.read_file('f1')
        assert s == content, '%s' % s
        s = self.read_file('backup.log').strip()
        ss = shlex.split(s)
        assert len(ss) == 3
        assert ss[2] == os.path.join(cwd,'f1')
        backup_path = self.get_backup_path(backup_dir,'f1')
        backup_path = os.path.join(backup_path,ss[1])
        s = self.read_file(backup_path)
        assert s == ''
