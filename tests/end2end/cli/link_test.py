#!/usr/bin/python

import os
import mock
import shlex
from nose.tools import istest

from tests.end2end.cli import common


class TestWithScratchdir(common.RunScratchContainer):
    @istest
    def copy_symlink(self):
        """
        E2E: Copy Symlink

        Runs a manifest which copies a symlink and verifies the contents of
        the destination link.
        """
        content = 'file { action copy source 1 target 2 }\n'
        self.write_file('1.man', content)
        fullname1 = self.get_fullname('1')
        fullname2 = self.get_fullname('2')
        man_fullname = self.get_fullname('1.man')
        os.symlink(man_fullname, fullname1)

        self.run_on_manifest('1.man')

        assert self.exists('2')
        s = self.read_file('2')
        assert s == content, '%s' % s
        assert os.path.islink(fullname2)
        assert os.readlink(fullname2) == man_fullname
