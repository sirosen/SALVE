import os
from nose.tools import istest

from tests import system


class TestWithScratchdir(system.RunScratchContainer):
    @istest
    def copy_single_file(self):
        """
        System: Copy a Single File

        Runs a manifest which copies itself and verifies the contents of
        the destination file.
        """
        content = 'file { action copy source 1.man target 2.man }\n'
        self.write_file('1.man', content)
        self.run_on_manifest('1.man')
        assert self.exists('2.man')
        s = self.read_file('2.man')
        assert s == content, '%s' % s

    @istest
    def implicit_copy_single_file(self):
        """
        System: Implicit Copy a Single File

        Runs a manifest which copies itself and verifies the contents of
        the destination file.
        """
        content = 'file { source 1.man target 2.man }\n'
        self.write_file('1.man', content)
        self.run_on_manifest('1.man')
        assert self.exists('2.man')
        s = self.read_file('2.man')
        assert s == content, '%s' % s

    @istest
    def copy_two_files(self):
        """
        System: Copy Two Files

        Runs a manifest which copies two files and verifies the contents of
        the destination files.
        """
        self.write_file('1.man',
                        'file { action copy source f1 target f1prime }\n' +
                        'file { source f2 target f2prime }\n')
        f1_content = 'alpha beta\n'
        f2_content = 'gamma\ndelta\n'
        self.write_file('f1', f1_content)
        self.write_file('f2', f2_content)

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
        System: Create a Single File

        Runs a manifest which creates a file and verifies the contents of
        the destination file are nil.
        """
        content = 'file { action create target f2 }\n'
        self.write_file('1.man', content)
        self.run_on_manifest('1.man')
        assert self.exists('f2')
        s = self.read_file('f2')
        assert s == '', '%s' % s

    @istest
    def create_multiple_files(self):
        """
        System: Create Multiple Files

        Runs a manifest which creates two files and verifies the contents of
        the destination file are nil.
        """
        content = ('file{action create target f2}\n' +
                   'file{action\ncreate target f3}')
        self.write_file('1.man', content)
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
        System: Create Existing File

        Runs a manifest which touches an existing file and verifies the
        contents of the destination file do not change.
        """
        content = 'file{action create target f1}\n'
        self.write_file('1.man', content)
        f1_content = 'alpha beta\n'
        self.write_file('f1', f1_content)
        self.run_on_manifest('1.man')
        assert self.exists('f1')
        s = self.read_file('f1')
        assert s == f1_content, '%s' % s

    @istest
    def change_file_permissions(self):
        """
        System: Change Single File Permissions

        Runs a manifest which touches several files and verifies the
        permissions of the target files.
        """
        content = 'file{action create target f1 mode 444}\n'
        self.write_file('1.man', content)
        self.run_on_manifest('1.man')
        assert self.exists('f1')
        s = self.read_file('f1')
        assert s == '', '%s' % s
        assert self.get_mode('f1') == int('444', 8)

    @istest
    def change_own_permissions(self):
        """
        System: Reflexive Manifest Permissions Change

        Runs a manifest which changes its own permissions to remove user
        read/write permissions.
        """
        content = 'file{action create target 1.man mode 066}\n'
        self.write_file('1.man', content)
        self.run_on_manifest('1.man')
        assert self.exists('1.man')
        assert self.get_mode('1.man') == int('066', 8)

    @istest
    def copy_unwritable_target(self):
        """
        System: Copy File, Unwritable Target

        Runs a manifest which copies itself over an unwritable target file.
        Should result in failure during verification.
        """
        content = 'file { action copy source 1.man target 2 }\n'
        self.write_file('1.man', content)
        self.write_file('2', '')

        fullname = self.get_fullname('2')
        os.chmod(fullname, 0o400)

        self.run_on_manifest('1.man')
        assert self.exists('2')
        s = self.read_file('2')
        assert s == '', s

        err = self.stderr.getvalue()
        expected1 = ('STARTUP [WARNING] ' +
                     'Deprecation Warning: --directory will be removed in ' +
                     'version 3 as --version3-relative-paths becomes the ' +
                     'default.')
        expected2 = (('VERIFICATION [WARNING] %s, line 1: FileCopy: ' +
                      'Non-Writable target file "%s"') %
                     (self.get_fullname('1.man'), fullname))
        assert expected1 in err, "%s doesn't contain %s" % (err, expected1)
        assert expected2 in err, "%s doesn't contain %s" % (err, expected2)

    @istest
    def copy_unreadable_source(self):
        """
        System: Copy File, Unreadable Source

        Runs a manifest which copies an unreadable source file.
        Should result in failure during verification.
        """
        content = 'file { action copy source 1 target 2 }\n'
        self.write_file('1.man', content)
        self.write_file('1', '')

        fullname = self.get_fullname('1')
        os.chmod(fullname, 0o200)

        self.run_on_manifest('1.man')
        assert not self.exists('2')

        err = self.stderr.getvalue()
        expected = (('VERIFICATION [WARNING] %s, line 1: FileCopy: ' +
                     'Non-Readable source file "%s"\n') %
                    (self.get_fullname('1.man'), fullname))
        assert expected in err, "%s\ndoesn't contain\n%s" % (err, expected)

    @istest
    def create_unwritable_target(self):
        """
        System: Create File, Existing Unwritable Target

        Runs a manifest which creates a file on top of an existing unwritable
        file.
        Should result in failure during verification due to unwritable target.
        """
        content = 'file { action create target a }\n'
        self.write_file('1.man', content)
        self.write_file('a', '')

        fullname = self.get_fullname('a')
        os.chmod(fullname, 0o400)

        self.run_on_manifest('1.man')

        err = self.stderr.getvalue()
        expected = (('VERIFICATION [WARNING] %s, line 1: FileCreate: ' +
                     'Non-Writable target file "%s"\n') %
                    (self.get_fullname('1.man'), fullname))
        assert expected in err, "%s\ndoesn't contain\n%s" % (err, expected)

    @istest
    def create_unwritable_parent(self):
        """
        System: Create File, Unwritable Parent Dir

        Runs a manifest which creates a file on in an existing unwritable
        directory.
        Should result in failure during verify due to unwritable target.
        """
        content = 'file { action create target a/b }\n'
        self.write_file('1.man', content)
        self.make_dir('a')

        fullname = self.get_fullname('a')
        fullname_b = self.get_fullname('a/b')
        os.chmod(fullname, 0o400)

        self.run_on_manifest('1.man')

        err = self.stderr.getvalue()
        expected = (('VERIFICATION [WARNING] %s, line 1: FileCreate: ' +
                     'Non-Writable target file "%s"\n') %
                    (self.get_fullname('1.man'), fullname_b))
        assert expected in err, "%s\ndoesn't contain\n%s" % (err, expected)

    @istest
    def create_with_v3_path(self):
        """
        System: Create File With v3 Relative Path

        Runs a manifest which creates a file, in version 3 relative path mode.
        """
        content = 'file gamma { action create }\n'
        self.make_dir('a')
        self.write_file('a/1.man', content)
        self.run_on_manifest('a/1.man')
        assert self.exists('gamma')
        s = self.read_file('gamma')
        assert s == '', s

        assert not self.exists('a/gamma')
        self.run_on_manifest('a/1.man', argv=['--ver3'])
        assert self.exists('a/gamma')
        s = self.read_file('a/gamma')
        assert s == '', s
