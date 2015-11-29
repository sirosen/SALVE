import os
from nose.tools import istest, eq_, ok_
from nose_parameterized import parameterized

from tests.framework import first_param_docfunc, assert_substr
from tests import system


class TestWithScratchdir(system.RunScratchContainer):
    @parameterized.expand(
        [('System: Copy an Empty Directory',
          'directory { action copy source a target b }\n'),
         ('System: Copy Directory Implicit Action',
          'directory { source a target b }\n')],
        testcase_func_doc=first_param_docfunc)
    @istest
    def parameterized_copy_dir_test(self, description, manifest_source):
        self.make_dir('a')
        content = manifest_source
        self.write_file('1.man', content)
        self.run_on_manifest('1.man')

        ok_(self.exists('b'))
        # make sure the original is unharmed
        ok_(self.exists('a'))
        eq_(len(self.listdir('b')), 0)

    @istest
    def create_dir(self):
        """
        System: Create a Directory

        Runs a manifest which copies an empty directory. Verifies that
        the target is created, and that it is empty as well.
        """
        content = 'directory { action create target a }\n'
        self.write_file('1.man', content)
        self.run_on_manifest('1.man')

        ok_(self.exists('a'))
        eq_(len(self.listdir('a')), 0)

    @istest
    def set_dir_mode(self):
        """
        System: Create a Directory to Set Mode

        Runs a manifest which copies an empty directory. Verifies that
        the target is created, and that it is empty as well.
        """
        self.make_dir('a')
        content = 'directory { action create target a mode 700 }\n'
        self.write_file('1.man', content)
        self.run_on_manifest('1.man')

        ok_(self.exists('a'))
        eq_(len(self.listdir('a')), 0)
        eq_(self.get_mode('a'), int('700', 8))

    @istest
    def copy_dir_with_file(self):
        """
        System: Copy Directory With File

        Runs a manifest which copies an directory containing one file.
        Verifies that the target is created, and that it has a duplicate
        of that file.
        """
        self.make_dir('p')
        content = 'directory { action copy source p target q }\n'
        self.write_file('1.man', content)
        self.write_file('p/alpha', 'string here!')
        self.run_on_manifest('1.man')

        ok_(self.exists('q'))
        # make sure the original is unharmed
        ok_(self.exists('p'))

        ls_result = self.listdir('q')
        eq_(len(ls_result), 1)
        eq_(ls_result[0], 'alpha')
        s = self.read_file('q/alpha').strip()
        eq_(s, 'string here!')

    @istest
    def copy_dir_containing_empty_dir(self):
        """
        System: Copy Directory Containing Empty Directory

        Runs a manifest which copies an directory containing an empty dir.
        Verifies that the target is created, and that it has a duplicate
        of the original dir contents.
        """
        self.make_dir('m/n')
        content = 'directory { action copy source m target m_prime }\n'
        self.write_file('manifest', content)
        self.run_on_manifest('manifest')

        ok_(self.exists('m_prime'))
        # make sure the original is unharmed
        ok_(self.exists('m'))
        ok_(self.exists('m/n'))

        ls_result = self.listdir('m_prime')
        eq_(len(ls_result), 1)
        eq_(ls_result[0], 'n')
        ls_result = self.listdir('m_prime/n')
        eq_(len(ls_result), 0)

    @istest
    def copy_unwritable_target_parent(self):
        """
        System: Copy Directory, Unwritable Target Parent

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

        ok_(self.exists('2'))
        ok_(not self.exists('2/1'))
        eq_(len(self.listdir('2')), 0)

        err = self.stderr.getvalue()
        expected = ('VERIFICATION [WARNING] %s, line 1: DirCreateAction: ' +
                    'Non-Writable target "%s"\n'
                    ) % (self.get_fullname('1.man'), fullname_sub)
        assert_substr(err, expected)
