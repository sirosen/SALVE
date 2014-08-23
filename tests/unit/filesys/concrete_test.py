#!/usr/bin/python

import os
import hashlib

import mock

from nose.tools import istest
from tests.utils.exceptions import ensure_except
from tests.utils.scratch import ScratchContainer

from salve.filesys import concrete
from salve.filesys import abstract


class TestWithScratchdir(ScratchContainer):
    @istest
    def missing_file_lookup(self):
        """
        Unit: Filesys Concrete Missing File Lookup Type Is None
        Verifies that attempting to lookup the type of a file that does not
        exist in a Concrete Filesystem will return None.
        """
        fs = concrete.Filesys()
        ty = fs.lookup_type(self.get_fullname('a'))
        assert ty is None

    @istest
    def file_lookup_type(self):
        """
        Unit: Filesys Concrete File Lookup Type Is FILE
        Validate that type lookups always produce the correct type.
        """
        full_path = self.get_fullname('a')
        self.write_file('a', 'abcdefg')
        fs = concrete.Filesys()
        ty = fs.lookup_type(full_path)
        assert ty is fs.element_types.FILE

    @istest
    def dir_lookup_type(self):
        """
        Unit: Filesys Concrete Dir Lookup Type Is DIR
        Validate that type lookups always produce the correct type.
        """
        full_path = self.get_fullname('a')
        self.make_dir('a')
        fs = concrete.Filesys()
        ty = fs.lookup_type(full_path)
        assert ty is fs.element_types.DIR

    @istest
    def link_lookup_type(self):
        """
        Unit: Filesys Concrete Link Lookup Is LINK
        Validate that type lookups always produce the correct type.
        """
        full_path = self.get_fullname('a')
        os.symlink('nowhere', full_path)
        fs = concrete.Filesys()
        ty = fs.lookup_type(full_path)
        assert ty is fs.element_types.LINK

    @istest
    def copy_file(self):
        """
        Unit: Filesys Concrete File Copy
        Copying a file must succeed.
        """
        content = 'fooing a bar in here'
        self.write_file('a', content)

        src_path = self.get_fullname('a')
        dst_path = self.get_fullname('b')

        fs = concrete.Filesys()
        fs.copy(src_path, dst_path)

        assert content == self.read_file('b')

    @istest
    def copy_link(self):
        """
        Unit: Filesys Concrete Link Copy
        Copying a symlink must succeed.
        """
        link_target = self.get_fullname('a')
        content = 'fooing a bar in here'
        self.write_file('a', content)

        src_path = self.get_fullname('a_link')
        dst_path = self.get_fullname('b')
        os.symlink(link_target, src_path)

        fs = concrete.Filesys()
        fs.copy(src_path, dst_path)

        assert os.path.islink(dst_path)
        assert os.readlink(dst_path) == link_target

    @istest
    def copy_dir(self):
        """
        Unit: Filesys Concrete Dir Copy
        Copying a directory must succeed.
        """
        self.make_dir('a/b/c')
        self.make_dir('z')

        content = 'fooing a bar in here'
        self.write_file('a/b/f1', content)

        src_path = self.get_fullname('a')
        dst_path = self.get_fullname('z/a')

        fs = concrete.Filesys()
        fs.copy(src_path, dst_path)

        assert os.path.isdir(dst_path)
        assert os.path.isfile(self.get_fullname('z/a/b/f1'))
        assert content == self.read_file('z/a/b/f1')

    @istest
    def create_file(self):
        """
        Unit: Filesys Concrete File Touch
        Creating an empty file must always work (when the path is valid)
        """
        full_path = self.get_fullname('a')

        fs = concrete.Filesys()
        fs.touch(full_path)

        assert os.path.isfile(full_path)
        assert '' == self.read_file('a')

    @istest
    def create_link(self):
        """
        Unit: Filesys Concrete Link Create
        Creating a symlink must always work, even if it is a broken link
        """
        full_path = self.get_fullname('a')
        link_target = 'b'

        fs = concrete.Filesys()
        fs.symlink(link_target, full_path)

        assert os.path.islink(full_path)
        assert link_target == os.readlink(full_path)

    @istest
    def create_dir_nonrecursive(self):
        """
        Unit: Filesys Concrete Dir Create (Non-Recursive)
        Creating a single level of a directory tree should always succeed
        """
        full_path = self.get_fullname('a')

        fs = concrete.Filesys()
        fs.mkdir(full_path, recursive=False)

        assert os.path.isdir(full_path)
        assert len(os.listdir(full_path)) == 0

    @istest
    def create_dir_recursive(self):
        """
        Unit: Filesys Concrete Dir Create (Recursive)
        Creating a path of a directory tree should always succeed if recursive
        is set.
        """
        full_path = self.get_fullname('a/b/c')

        fs = concrete.Filesys()
        fs.mkdir(full_path, recursive=True)

        assert os.path.isdir(full_path)
        assert len(os.listdir(full_path)) == 0

    @istest
    def double_create_dir(self):
        """
        Unit: Filesys Concrete Dir Double Create No Error
        Repeated creation of a single directory should not raise any errors
        """
        full_path = self.get_fullname('a')

        fs = concrete.Filesys()
        fs.mkdir(full_path, recursive=False)
        fs.mkdir(full_path, recursive=False)

        assert os.path.isdir(full_path)
        assert len(os.listdir(full_path)) == 0

    @istest
    def create_dir_nonrecursive_missing_parent(self):
        """
        Unit: Filesys Concrete Dir Create (Non-Recursive) Missing Parent Error
        Validates that creating a directory with recursive off raises an
        OSError with errno=2 if there is a missing ancestor.
        """
        full_path = self.get_fullname('a/b')

        fs = concrete.Filesys()
        e = ensure_except(OSError, fs.mkdir, full_path, recursive=False)

        assert e.errno == 2
        assert not os.path.isdir(full_path)

    @istest
    def file_open_write_only(self):
        """
        Unit: Filesys Concrete File Open Write-Only
        Verifies that opening a file in write only mode works as expected
        """
        full_path = self.get_fullname('a')

        fs = concrete.Filesys()
        fs.touch(full_path)

        with fs.open(full_path, 'w') as fd:
            fd.write('xyz')
            ensure_except(IOError, fd.read)

        assert os.path.isfile(full_path)
        assert 'xyz' == self.read_file('a')

    @istest
    def file_open_read_only(self):
        """
        Unit: Filesys Concrete File Open Read-Only
        Verifies that opening a file in read only mode works as expected
        """
        full_path = self.get_fullname('a')
        self.write_file('a', 'xyz')

        fs = concrete.Filesys()
        fs.touch(full_path)

        with fs.open(full_path, 'r') as fd:
            ensure_except(IOError, fd.write, 'pqr')
            assert fd.read() == 'xyz'

    @istest
    def file_get_hash(self):
        """
        Unit: Filesys Concrete File Get Hash
        Validates the result of getting a file's sha512 hash
        """
        full_path = self.get_fullname('a')
        self.write_file('a', 'xyz')

        fs = concrete.Filesys()

        hashval = fs.hash(full_path)
        expect = hashlib.sha512('xyz'.encode('utf-8')).hexdigest()
        assert hashval == expect

    @istest
    def link_get_hash(self):
        """
        Unit: Filesys Concrete Link Get Hash
        Validates the result of getting a symlink's sha256 hash
        """
        full_path = self.get_fullname('a')

        fs = concrete.Filesys()
        fs.symlink('xyz', full_path)

        hashval = fs.hash(full_path)
        expect = hashlib.sha256('xyz'.encode('utf-8')).hexdigest()
        assert hashval == expect

    @istest
    def concrete_access_all_combinations(self):
        """
        Unit: Filesys Concrete Access With All Flags & Perms
        Validates that the various valid inputs to access return the correct
        results. Only uses user perms, setting g and o to 0.
        """
        # maps (flags, mode) pairs to the expected results
        # when mode=None, means the file is missing
        result_map = {}
        all_modes = [0o000, 0o100, 0o200, 0o400,
                0o300, 0o500, 0o600, 0o700]

        for mode in all_modes:
            result_map[(os.F_OK, mode)] = True
            r = mode & 0o400 != 0
            w = mode & 0o200 != 0
            x = mode & 0o100 != 0
            result_map[(os.R_OK, mode)] = r
            result_map[(os.W_OK, mode)] = w
            result_map[(os.X_OK, mode)] = x
            result_map[(os.R_OK | os.W_OK, mode)] = r and w
            result_map[(os.R_OK | os.X_OK, mode)] = r and x
            result_map[(os.W_OK | os.X_OK, mode)] = w and x
            result_map[(os.R_OK | os.W_OK | os.X_OK, mode)] = r and w and x

        # somewhat redundant, but an easy way to list all flags
        for flags in (os.F_OK, os.R_OK, os.W_OK, os.X_OK,
                os.R_OK | os.W_OK, os.R_OK | os.X_OK, os.W_OK | os.X_OK,
                os.R_OK | os.W_OK | os.X_OK):
            result_map[(flags, None)] = False

        fs = concrete.Filesys()

        for (flags, mode) in result_map:
            expect = result_map[(flags, mode)]

            full_path = self.get_fullname('a')

            if mode is not None:
                fs.touch(full_path)
                fs.chmod(full_path, mode)

            assert fs.access(full_path, flags) == expect

            if mode is not None:
                os.remove(full_path)

    @istest
    def file_stat(self):
        """
        Unit: Filesys Concrete File Stat
        Verifies that stating a file gives an object with the correct
        attributes.
        """
        full_name = self.get_fullname('a')
        fs = concrete.Filesys()
        assert not fs.exists(full_name)

        fs.touch(full_name)

        st_result = fs.stat(full_name)

        assert hasattr(st_result, 'st_mode')
        assert hasattr(st_result, 'st_ino')
        assert hasattr(st_result, 'st_nlink')
        assert hasattr(st_result, 'st_uid')
        assert hasattr(st_result, 'st_gid')
        assert hasattr(st_result, 'st_size')
        assert hasattr(st_result, 'st_atime')
        assert hasattr(st_result, 'st_mtime')
        assert hasattr(st_result, 'st_ctime')

        assert st_result.st_uid == os.geteuid()
        assert st_result.st_gid == os.getegid()

    @istest
    def link_stat(self):
        """
        Unit: Filesys Concrete Link Stat
        Verifies that attempting to stat a link works.
        """
        full_name = self.get_fullname('a')
        fs = concrete.Filesys()
        assert not fs.exists(full_name)

        fs.symlink('nowhere', full_name)

        st_result = fs.stat(full_name)

        assert hasattr(st_result, 'st_mode')
        assert hasattr(st_result, 'st_ino')
        assert hasattr(st_result, 'st_nlink')
        assert hasattr(st_result, 'st_uid')
        assert hasattr(st_result, 'st_gid')
        assert hasattr(st_result, 'st_size')
        assert hasattr(st_result, 'st_atime')
        assert hasattr(st_result, 'st_mtime')
        assert hasattr(st_result, 'st_ctime')

        assert st_result.st_uid == os.geteuid()
        assert st_result.st_gid == os.getegid()

    @istest
    def file_chmod(self):
        """
        Unit: Filesys Concrete File Chmod
        Verifies that chmoding a file results in correct stat() results for
        various permissions settings.
        """
        full_name = self.get_fullname('a')
        fs = concrete.Filesys()
        assert not fs.exists(full_name)

        fs.touch(full_name)
        fs.chmod(full_name, 0o651)

        st_result = fs.stat(full_name)
        assert hasattr(st_result, 'st_mode')
        assert st_result.st_mode & 0o777 == 0o651, oct(st_result.st_mode)

        full_name = self.get_fullname('b')
        assert not fs.exists(full_name)

        fs.touch(full_name)
        fs.chmod(full_name, 0o536)

        st_result = fs.stat(full_name)
        assert hasattr(st_result, 'st_mode')
        assert st_result.st_mode & 0o777 == 0o536, oct(st_result.st_mode)

    @istest
    def file_chown(self):
        """
        Unit: Filesys Concrete File Chown
        Verifies that file chowns pass through to lchown. Because we cannot
        guarantee that the tests are run as root, we have no expectation that a
        chown operation will work.
        """
        full_name = self.get_fullname('a')
        fs = concrete.Filesys()
        fs.touch(full_name)

        mock_chown = mock.Mock()
        mock_chown.return_value = None

        with mock.patch('os.lchown', mock_chown):
            fs.chown(full_name, 100, 200)

        mock_chown.assert_called_once_with(full_name, 100, 200)

    @istest
    def dir_walk(self):
        """
        Unit: Filesys Concrete Dir Walk
        Validates the results of using filesys tooling to create a directory
        and walk it.
        """
        fs = concrete.Filesys()
        fs.mkdir(self.get_fullname('a/b/c'))
        fs.touch(self.get_fullname('a/f1'))
        fs.symlink('../f1', self.get_fullname('a/b/l1'))
        fs.symlink('..', self.get_fullname('a/b/c/l2'))

        results = []
        for (d, sds, fs) in fs.walk(self.get_fullname('a')):
            results.append((d, sds, fs))

        assert len(results) == 3
        assert results[0] == (self.get_fullname('a'), ['b'], ['f1'])
        assert results[1] == (self.get_fullname('a/b'), ['c'], ['l1'])
        assert results[2] == (self.get_fullname('a/b/c'), ['l2'], [])

    @istest
    def dir_create_bad_permissions_fails(self):
        """
        Unit: Filesys Concrete Dir Create Bad Permissions Fails
        Creating a directory when the parent directory has bad permissions
        should raise an OSError.
        """
        fs = concrete.Filesys()
        full_name = self.get_fullname('a')
        fs.mkdir(full_name)
        fs.chmod(full_name, 0o000)

        full_name = self.get_fullname('a/b')
        e = ensure_except(OSError, fs.mkdir, full_name)
        # must be a permission denied error
        assert e.errno == 13
