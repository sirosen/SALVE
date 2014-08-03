#!/usr/bin/python

import os
import hashlib

import mock

from nose.tools import istest
from tests.utils.exceptions import ensure_except
from tests.utils.scratch import ScratchContainer

from salve.filesys import concrete
from salve.filesys import abstract


@istest
def filesyselement_is_abstract():
    """
    Unit: Filesys Concrete FilesysElement Base Class Is Abstract
    Ensures that a Concrete FilesysElement cannot be instantiated.
    """
    ensure_except(TypeError, concrete.FilesysElement, '/dummy/path')


class TestWithScratchdir(ScratchContainer):
    @istest
    def missing_file_lookup(self):
        """
        Unit: Filesys Concrete Missing File Lookup Is None
        Verifies that attempting to lookup a file that does not exist in a
        Concrete Filesystem will return None.
        """
        fs = concrete.Filesys()
        elem = fs.lookup(self.get_fullname('a'))
        assert elem is None

    @istest
    def registered_elem_lookup_generator(self):
        """
        Validate registered element lookups with each concrete type.
        They should always return the registered element (not a new element).
        """
        # map types to names for test names
        tynames = {
                concrete.File: 'File',
                concrete.Link: 'Link',
                concrete.Dir: 'Dir'
                }

        for ty in tynames:
            def func():
                full_path = self.get_fullname('a')
                elem = ty(full_path)
                fs = concrete.Filesys()
                fs.register(elem)
                elem2 = fs.lookup(full_path)

                assert elem2 is not None
                assert isinstance(elem2, ty)
                assert elem is elem2

            name = tynames[ty]
            func.description = ('Unit: Filesys Concrete Registered ' +
                    '%s Lookup Succeeds' % name)

            yield func

    @istest
    def unregistered_file_lookup_generator(self):
        """
        Validate file element lookups on an existing (unregistered) file with
        each concrete type's Constructor, and with no constructor.
        They should always return a new element.
        """
        # map types to names for test names
        tynames = {
                concrete.File: ' (With File Constructor)',
                concrete.Link: ' (With Link Constructor)',
                concrete.Dir: ' (With Dir Constructor)',
                abstract.File: ' (With Abstract File Constructor)',
                abstract.Link: ' (With Abstract Link Constructor)',
                abstract.Dir: ' (With Abstract Dir Constructor)',
                None: ''
                }

        for ty in tynames:
            def func():
                full_path = self.get_fullname('a')
                self.write_file('a', 'nonsense')

                fs = concrete.Filesys()
                elem = fs.lookup(full_path, elem_type=ty)

                assert elem is not None
                assert elem.path == full_path
                assert isinstance(elem, concrete.File)

            constructor_string = tynames[ty]
            func.description = ('Unit: Filesys Concrete Unregistered ' +
                    'File Lookup%s Succeeds' % constructor_string)

            yield func

    @istest
    def unregistered_symlink_lookup_generator(self):
        """
        Validate link element lookups on an existing (unregistered) link with
        each concrete type's Constructor, and with no constructor.
        They should always return a new element.
        """
        # map types to names for test names
        tynames = {
                concrete.File: ' (With File Constructor)',
                concrete.Link: ' (With Link Constructor)',
                concrete.Dir: ' (With Dir Constructor)',
                abstract.File: ' (With Abstract File Constructor)',
                abstract.Link: ' (With Abstract Link Constructor)',
                abstract.Dir: ' (With Abstract Dir Constructor)',
                None: ''
                }

        for ty in tynames:
            def func():
                full_path = self.get_fullname('a')
                os.symlink('nowhere', full_path)

                fs = concrete.Filesys()
                elem = fs.lookup(full_path, elem_type=ty)

                assert elem is not None
                assert elem.path == full_path
                assert isinstance(elem, concrete.Link)

                # no magic cleanup happens in generators
                os.remove(full_path)

            constructor_string = tynames[ty]
            func.description = ('Unit: Filesys Concrete Unregistered ' +
                    'Link Lookup%s Succeeds' % constructor_string)

            yield func

    @istest
    def unregistered_dir_lookup_generator(self):
        """
        Validate dir element lookups on an existing (unregistered) dir with
        each concrete type's Constructor, and with no constructor.
        They should always return a new element.
        """
        # map types to names for test names
        tynames = {
                concrete.File: ' (With File Constructor)',
                concrete.Link: ' (With Link Constructor)',
                concrete.Dir: ' (With Dir Constructor)',
                abstract.File: ' (With Abstract File Constructor)',
                abstract.Link: ' (With Abstract Link Constructor)',
                abstract.Dir: ' (With Abstract Dir Constructor)',
                None: ''
                }

        for ty in tynames:
            def func():
                full_path = self.get_fullname('a')
                self.make_dir('a')

                fs = concrete.Filesys()
                elem = fs.lookup(full_path, elem_type=ty)

                assert elem is not None
                assert elem.path == full_path
                assert isinstance(elem, concrete.Dir)

                # no magic cleanup happens in generators
                os.rmdir(full_path)

            constructor_string = tynames[ty]
            func.description = ('Unit: Filesys Concrete Unregistered ' +
                    'Dir Lookup%s Succeeds' % constructor_string)

            yield func

    @istest
    def unregistered_missing_elem_lookup_generator(self):
        """
        Validate unregistered element lookups with each concrete type when the
        object is missing from the underlying filesystem.
        They should always return a new element.
        """
        # map types to names for test names
        tynames = {
                concrete.File: 'File',
                concrete.Link: 'Link',
                concrete.Dir: 'Dir'
                }

        for ty in tynames:
            def func():
                full_path = self.get_fullname('a')
                fs = concrete.Filesys()
                elem = fs.lookup(full_path, elem_type=ty)

                assert elem.path == full_path
                assert not elem.exists()
                assert isinstance(elem, ty)

            name = tynames[ty]
            func.description = ('Unit: Filesys Concrete Unregistered ' +
                    'Missing %s Lookup (With Creation) Succeeds' % name)

            yield func

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

        f = concrete.File(full_path)
        f.touch()

        assert os.path.isfile(full_path)
        assert '' == self.read_file('a')

    @istest
    def agnostic_create_file(self):
        """
        Unit: Filesys Concrete File Agnostic Create
        Creating an empty file must always work (when the path is valid), and
        should be identical to touch()
        """
        full_path = self.get_fullname('a')

        f = concrete.File(full_path)
        f.create()

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

        l = concrete.Link(full_path)
        l.symlink(link_target)

        assert os.path.islink(full_path)
        assert link_target == os.readlink(full_path)

    @istest
    def agnostic_create_link(self):
        """
        Unit: Filesys Concrete Link Agnostic Create
        Creating a symlink must always work, even if it is a broken link,
        should be identical to symlink()
        """
        full_path = self.get_fullname('a')
        link_target = 'b'

        l = concrete.Link(full_path)
        l.create(link_target)

        assert os.path.islink(full_path)
        assert link_target == os.readlink(full_path)

    @istest
    def create_dir_nonrecursive(self):
        """
        Unit: Filesys Concrete Dir Create (Non-Recursive)
        Creating a single level of a directory tree should always succeed
        """
        full_path = self.get_fullname('a')

        d = concrete.Dir(full_path)
        d.mkdir(recursive=False)

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

        d = concrete.Dir(full_path)
        d.mkdir(recursive=True)

        assert os.path.isdir(full_path)
        assert len(os.listdir(full_path)) == 0

    @istest
    def agnostic_create_dir_nonrecursive(self):
        """
        Unit: Filesys Concrete Dir Agnostic Create (Non-Recursive)
        Creating a single level of a directory tree should always succeed
        Should be identical to mkdir()
        """
        full_path = self.get_fullname('a')

        d = concrete.Dir(full_path)
        d.create(recursive=False)

        assert os.path.isdir(full_path)
        assert len(os.listdir(full_path)) == 0

    @istest
    def agnostic_create_dir_recursive(self):
        """
        Unit: Filesys Concrete Dir Agnostic Create (Recursive)
        Creating a path of a directory tree should always succeed if recursive
        is set.
        Should be identical to mkdir()
        """
        full_path = self.get_fullname('a/b/c')

        d = concrete.Dir(full_path)
        d.create(recursive=True)

        assert os.path.isdir(full_path)
        assert len(os.listdir(full_path)) == 0

    @istest
    def double_create_dir(self):
        """
        Unit: Filesys Concrete Dir Double Create No Error
        Repeated creation of a single directory should not raise any errors
        """
        full_path = self.get_fullname('a')

        d = concrete.Dir(full_path)
        d.mkdir(recursive=False)
        d.mkdir(recursive=False)

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

        d = concrete.Dir(full_path)
        e = ensure_except(OSError, d.mkdir, recursive=False)

        assert e.errno == 2
        assert not os.path.isdir(full_path)

    @istest
    def file_open_write_only(self):
        """
        Unit: Filesys Concrete File Open Write-Only
        Verifies that opening a file in write only mode works as expected
        """
        full_path = self.get_fullname('a')

        f = concrete.File(full_path)
        f.touch()

        with f.open('w') as fd:
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

        f = concrete.File(full_path)

        with f.open('r') as fd:
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

        f = concrete.File(full_path)

        hashval = f.hash()
        expect = hashlib.sha512('xyz'.encode('utf-8')).hexdigest()
        assert hashval == expect

    @istest
    def link_get_hash(self):
        """
        Unit: Filesys Concrete Link Get Hash
        Validates the result of getting a symlink's sha256 hash
        """
        full_path = self.get_fullname('a')

        f = concrete.Link(full_path)
        f.symlink('xyz')

        hashval = f.hash()
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

        for (flags, mode) in result_map:
            expect = result_map[(flags, mode)]

            full_path = self.get_fullname('a')
            elem = concrete.File(full_path)

            if mode is not None:
                elem.touch()
                os.chmod(full_path, mode)

            assert elem.access(flags) == expect

            if mode is not None:
                os.remove(full_path)

    @istest
    def file_stat(self):
        """
        Unit: Filesys Concrete File Stat
        Verifies that stating a file gives an object with the correct
        attributes.
        """
        fs = concrete.Filesys()
        elem = fs.lookup(self.get_fullname('a'), elem_type=concrete.File)
        assert elem is not None

        elem.create()

        st_result = elem.stat()

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
        fs = concrete.Filesys()
        elem = fs.lookup(self.get_fullname('a'), elem_type=concrete.Link)
        assert elem is not None

        elem.create('nowhere')

        st_result = elem.stat()

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
        fs = concrete.Filesys()

        elem = fs.lookup(self.get_fullname('a'), elem_type=concrete.File)
        elem.create()
        elem.chmod(0o651)

        st_result = elem.stat()
        assert hasattr(st_result, 'st_mode')
        assert st_result.st_mode & 0o777 == 0o651, oct(st_result.st_mode)

        elem = fs.lookup(self.get_fullname('b'), elem_type=concrete.File)
        elem.create()
        elem.chmod(0o536)

        st_result = elem.stat()
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
        fs = concrete.Filesys()

        elem = fs.lookup(self.get_fullname('a'), elem_type=concrete.File)
        elem.create()

        def mock_chown(path, uid, gid):
            global mock_args
            mock_args = (path, uid, gid)

        with mock.patch('os.lchown', mock_chown):
            elem.chown(100, 200)

        assert mock_args == (elem.path, 100, 200)

    @istest
    def dir_walk(self):
        """
        Unit: Filesys Concrete Dir Walk
        Validates the results of using filesys tooling to create a directory
        and walk it.
        """
        fs = concrete.Filesys()
        elem = fs.lookup(self.get_fullname('a/b/c'), elem_type=concrete.Dir)
        elem.create(recursive=True)

        elem = fs.lookup(self.get_fullname('a/f1'), elem_type=concrete.File)
        elem.create()

        elem = fs.lookup(self.get_fullname('a/b/l1'), elem_type=concrete.Link)
        elem.create('../f1')

        elem = fs.lookup(self.get_fullname('a/b/c/l2'),
                elem_type=concrete.Link)
        elem.create('..')

        elem = fs.lookup(self.get_fullname('a'))
        results = []
        for (d, sds, fs) in elem.walk():
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
        elem = fs.lookup(self.get_fullname('a'), elem_type=concrete.Dir)
        elem.create()
        elem.chmod(0o000)

        elem = fs.lookup(self.get_fullname('a/b'), elem_type=concrete.Dir)
        e = ensure_except(OSError, elem.create)
        # must be a permission denied error
        assert e.errno == 13
