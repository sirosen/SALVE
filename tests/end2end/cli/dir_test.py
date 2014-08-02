#!/usr/bin/python

import os
import mock
from nose.tools import istest

from tests.end2end.cli import common


class TestWithScratchdir(common.RunScratchContainer):
    @istest
    def copy_empty_dir(self):
        """
        E2E: Copy an Empty Directory

        Runs a manifest which copies an empty directory. Verifies that
        the target is created, and that it is empty as well.
        """
        self.make_dir('a')
        content = 'directory { action copy source a target b }\n'
        self.write_file('1.man', content)
        self.run_on_manifest('1.man')

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
        self.write_file('1.man', content)
        self.run_on_manifest('1.man')

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
        self.write_file('1.man', content)
        self.run_on_manifest('1.man')

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
        self.write_file('1.man', content)
        self.run_on_manifest('1.man')

        assert self.exists('a')
        assert len(self.listdir('a')) == 0
        assert self.get_mode('a') == int('700', 8)

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
        self.write_file('1.man', content)
        self.write_file('p/alpha', 'string here!')
        self.run_on_manifest('1.man')

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
        self.write_file('manifest', content)
        self.run_on_manifest('manifest')

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
    def copy_unwritable_target_parent(self):
        """
        E2E: Copy Directory, Unwritable Target Parent

        Runs a manifest which copies a dir to an unwritable location.
        Should result in failure during verification.
        """
        content = 'directory { action copy source 1 target 2/1 }\n'
        self.write_file('1.man', content)
        self.make_dir('1')
        self.make_dir('2')

        fullname = self.get_fullname('2')
        fullname_sub = self.get_fullname('2/1')
        os.chmod(fullname, 0o400)

        self.run_on_manifest('1.man')

        assert self.exists('2')
        assert not self.exists('2/1')
        assert len(self.listdir('2')) == 0

        err = self.stderr.getvalue()
        expected = ('[WARN] [VERIFICATION] %s, line 1: DirCreate: ' +
            'Non-Writable target dir "%s"\n'
            ) % (self.get_fullname('1.man'), fullname_sub)
        assert expected in err, "%s\ndoesn't contain\n%s" % (err, expected)
