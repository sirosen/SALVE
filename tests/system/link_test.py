import os
from nose.tools import istest, eq_, ok_

from tests import system


class TestWithScratchdir(system.RunScratchContainer):
    @istest
    def copy_symlink(self):
        """
        System: Copy Symlink

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

        ok_(self.exists('2'))
        s = self.read_file('2')
        eq_(s, content)
        ok_(os.path.islink(fullname2))
        eq_(os.readlink(fullname2), man_fullname)
