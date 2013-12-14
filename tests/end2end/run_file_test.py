#!/usr/bin/python

from nose.tools import istest, with_setup
import mock, os

import src.run.command
import tests.utils.scratch as scratch

def run_on_args(argv):
    with mock.patch('sys.argv',argv):
        return src.run.command.main()

class TestWithScratchdir():
    def setUp(self):
        scratch.make_scratch(self)
    def tearDown(self):
        scratch.rm_scratch(self)

    @istest
    def copy_single_file(self):
        """
        E2E: Copy a Single File

        Runs a manifest which copies itself and verifies the contents of
        the destination file.
        """
        cwd = self.scratch_dir
        content = 'file { action copy source 1.man target 2.man }\n'
        scratch.write_scratchfile(self,'1.man',content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])
        assert os.path.exists(os.path.join(cwd,'2.man'))
        s = scratch.read_scratchfile(self,'2.man')
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
        scratch.write_scratchfile(self,'1.man',content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])
        assert os.path.exists(os.path.join(cwd,'2.man'))
        s = scratch.read_scratchfile(self,'2.man')
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
        scratch.write_scratchfile(self,'1.man',
            'file { action copy source f1 target f1prime }\n'+\
            'file { source f2 target f2prime }\n'
            )
        f1_content = 'alpha beta\n'
        f2_content = 'gamma\ndelta\n'
        scratch.write_scratchfile(self,'f1',f1_content)
        scratch.write_scratchfile(self,'f2',f2_content)

        run_on_args(['./salve.py','-m',man_path])

        assert os.path.exists(os.path.join(cwd,'f1prime'))
        assert os.path.exists(os.path.join(cwd,'f2prime'))
        s = scratch.read_scratchfile(self,'f1prime')
        assert s == f1_content, '%s' % s
        s = scratch.read_scratchfile(self,'f2prime')
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
        scratch.write_scratchfile(self,'1.man',content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])
        assert os.path.exists(os.path.join(cwd,'f2'))
        s = scratch.read_scratchfile(self,'f2')
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
        scratch.write_scratchfile(self,'1.man',content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])
        assert os.path.exists(os.path.join(cwd,'f2'))
        assert os.path.exists(os.path.join(cwd,'f3'))
        s = scratch.read_scratchfile(self,'f2')
        assert s == '', '%s' % s
        s = scratch.read_scratchfile(self,'f3')
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
        scratch.write_scratchfile(self,'1.man',content)
        f1_content = 'alpha beta\n'
        scratch.write_scratchfile(self,'f1',f1_content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])
        assert os.path.exists(os.path.join(cwd,'f1'))
        s = scratch.read_scratchfile(self,'f1')
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
        scratch.write_scratchfile(self,'1.man',content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])
        assert os.path.exists(os.path.join(cwd,'f1'))
        s = scratch.read_scratchfile(self,'f1')
        assert s == '', '%s' % s
        assert scratch.get_scratchfile_mode(self,'f1') == int('444',8)

    @istest
    def change_own_permissions(self):
        """
        E2E: Reflexive Manifest Permissions Change

        Runs a manifest which changes its own permissions to remove user
        read/write permissions.
        """
        cwd = self.scratch_dir
        content = 'file{action create target 1.man mode 066}\n'
        scratch.write_scratchfile(self,'1.man',content)
        man_path = os.path.join(cwd,'1.man')
        run_on_args(['./salve.py','-m',man_path])
        assert os.path.exists(os.path.join(cwd,'1.man'))
        assert scratch.get_scratchfile_mode(self,'1.man') == int('066',8)
