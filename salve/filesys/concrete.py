#!/usr/bin/python

import os
import shutil
import abc
from contextlib import contextmanager

from salve.filesys import abstract
from salve.util import with_metaclass, hash_from_path


class Filesys(abstract.Filesys):
    def lookup_type(self, path):
        """
        Lookup the type of a given path.

        Args:
            @path
            The path to the file, dir, or link to lookup.
        """
        # if no constructor is given, inspect the underlying filesystem
        if os.path.islink(path):
            return self.element_types.LINK
        elif os.path.isdir(path):
            return self.element_types.DIR
        elif os.path.isfile(path):
            return self.element_types.FILE
        else:
            return None

    def access(self, path, mode):
        """
        Transparent implementation of access() using os.access

        Args:
            @mode
            The type of access being inspected
        """
        return os.access(path, mode)

    def stat(self, path):
        """
        Transparent implementation of stat() using os.lstat
        """
        return os.lstat(path)

    def chmod(self, path, *args, **kwargs):
        """
        Transparent implementation of chmod() using os.chmod
        """
        return os.chmod(path, *args, **kwargs)

    def chown(self, path, uid, gid):
        """
        Transparent implementation of chown() using os.lchown
        """
        return os.lchown(path, uid, gid)

    def exists(self, path):
        """
        Transparent implementation of exists() using os.path.lexists
        """
        return os.path.lexists(path)

    def hash(self, path):
        """
        Transparent implementation of hash() using
        salve.util.hash_from_path
        """
        assert self.exists(path)
        return hash_from_path(path)

    def copy(self, src, dst):
        """
        Copies the source to the destination on the underlying filesys. Does
        not necessarily create a new entry registered to the destination.

        Args:
            @src
            The origin path to be copied. When looked up in the filesys, must
            not be None and must satisfy exists()

            @dst
            The destination path for the copy operation. The ancestors of this
            path must exist so that the file creation will not fail.
        """
        assert self.exists(src)

        src_ty = self.lookup_type(src)
        if src_ty == self.element_types.FILE:
            shutil.copyfile(src, dst)
        # FIXME: copytree is kind of scary. Eventually would like to replace
        # this with a NotImplementedError in order to force explicit creates
        # and file copies
        elif src_ty == self.element_types.DIR:
            shutil.copytree(src, dst, symlinks=True)
        elif src_ty == self.element_types.LINK:
            os.symlink(os.readlink(src), dst)
        else:  # pragma: no cover
            assert False

    @contextmanager
    def open(self, path, *args, **kwargs):
        """
        Transparent implementation of open() using builtin open
        """
        with open(path, *args, **kwargs) as f:
            yield f

    def touch(self, path, *args, **kwargs):
        """
        Touch a file by opening it in append mode and closing it
        """
        with self.open(path, 'a') as f:
            pass

    def symlink(self, path, target):
        """
        Transparent implementation of symlink() using os.symlink
        """
        os.symlink(path, target)

    def walk(self, path, *args, **kwargs):
        """
        Transparent implementation of walk() using os.walk
        """
        for x in os.walk(path, *args, **kwargs):
            yield x

    def mkdir(self, path, recursive=True):
        """
        Use os.mkdir or os.makedirs to create the directory desired,
        suppressing "already exists" errors.
        May still return OSError(2, 'No such file or directory') when
        nonrecursive mkdir calls have missing ancestors.
        """
        try:
            if recursive:
                os.makedirs(path)
            else:
                os.mkdir(path)
        except OSError as e:
            # 'File exists' errno
            if e.errno == 17:
                return
            else:
                raise e

    def get_existing_ancestor(self, path):
        """
        Finds the longest prefix to a path that is known to exist.

        Args:
            @path
            An absolute path whose prefix should be inspected.
        """
        # be safe
        path = os.path.abspath(path)
        # exists is sufficient because we can stat directories as long as
        # we have execute permissions
        while not os.path.exists(path):
            path = os.path.dirname(path)
        return path
