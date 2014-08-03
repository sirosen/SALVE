#!/usr/bin/python

import os
import shutil
import abc
from contextlib import contextmanager

from salve.filesys import abstract
from salve.util.six import with_metaclass


class FilesysElement(with_metaclass(abc.ABCMeta, abstract.FilesysElement)):
    def access(self, mode):
        """
        Transparent implementation of access() using os.access

        Args:
            @mode
            The type of access being inspected
        """
        return os.access(self.path, mode)

    def stat(self):
        """
        Transparent implementation of stat() using os.lstat
        """
        return os.lstat(self.path)

    def chmod(self, *args, **kwargs):
        """
        Transparent implementation of chmod() using os.chmod
        """
        return os.chmod(self.path, *args, **kwargs)

    def chown(self, uid, gid):
        """
        Transparent implementation of chown() using os.lchown
        """
        return os.lchown(self.path, uid, gid)

    def exists(self):
        """
        Transparent implementation of exists() using os.path.lexists
        """
        return os.path.lexists(self.path)

    def hash(self):
        """
        Transparent implementation of hash() using
        salve.util.streams.hash_by_filename
        """
        from salve.util.streams import hash_by_filename
        assert self.exists()
        return hash_by_filename(self.path)


class File(FilesysElement, abstract.File):
    @contextmanager
    def open(self, *args, **kwargs):
        """
        Transparent implementation of open() using builtin open
        """
        with open(self.path, *args, **kwargs) as f:
            yield f

    def touch(self, *args, **kwargs):
        """
        Touch a file by opening it in append mode and closing it
        """
        with self.open('a') as f:
            pass


class Link(FilesysElement, abstract.Link):
    def symlink(self, path):
        """
        Transparent implementation of symlink() using os.symlink
        """
        os.symlink(path, self.path)


class Dir(FilesysElement, abstract.Dir):
    def walk(self, *args, **kwargs):
        """
        Transparent implementation of walk() using os.walk
        """
        for x in os.walk(self.path, *args, **kwargs):
            yield x

    def mkdir(self, recursive=True):
        """
        Use os.mkdir or os.makedirs to create the directory desired,
        suppressing "already exists" errors.
        May still return OSError(2, 'No such file or directory') when
        nonrecursive mkdir calls have missing ancestors.
        """
        try:
            if recursive:
                os.makedirs(self.path)
            else:
                os.mkdir(self.path)
        except OSError as e:
            # 'File exists' errno
            if e.errno == 17:
                return
            else:
                raise e


class Filesys(abstract.Filesys):
    def __init__(self):
        """
        Initialize a new Concrete Filesys representation.
        """
        # the lookup_table maps paths to FilesysElements
        self.lookup_table = {}

    def register(self, elem):
        """
        Registers an element to the filesystem for future lookups.

        Args:
            @elem
            The element to register. Its path attribute will be inspected for
            the purpose of registration.
        """
        self.lookup_table[elem.path] = elem

    def lookup(self, path, elem_type=None):
        """
        Lookup the element registered to @path, possibly constructing a new
        element to register if necessary.

        Args:
            @path
            The path to the file, dir, or link to lookup.

        KWArgs:
            @elem_type=None
            The class or constructor to use if the initial lookup fails. None
            means that no constructor will be used. May be an abstract class,
            in which case the matching concrete version will be used.
        """
        # if there is a registered element, return it
        if path in self.lookup_table:
            return self.lookup_table[path]

        # if no constructor is given, inspect the underlying filesystem
        elif os.path.islink(path):
            return Link(path)
        elif os.path.isdir(path):
            return Dir(path)
        elif os.path.isfile(path):
            return File(path)
        # if there is a constructor given for an unregistered element,
        # then register a new element of that type, and return it
        elif elem_type is not None:
            if issubclass(elem_type, abstract.File):
                self.register(File(path))
            elif issubclass(elem_type, abstract.Link):
                self.register(Link(path))
            elif issubclass(elem_type, abstract.Dir):
                self.register(Dir(path))
            # short-circuit if none of these are a match
            else:
                return None
            # if this raises a KeyError, this is an internal error in the
            # concrete filesys usage -- the element registered must match the
            # path -- so don't try to catch it if raised
            return self.lookup_table[path]

        # if there is no given element, and no constructor supplied, then
        # return None, meaning that the lookup failed to "find" an element
        else:
            return None

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
        src_elem = self.lookup(src)
        assert src_elem is not None
        assert src_elem.exists()

        if isinstance(src_elem, File):
            shutil.copyfile(src, dst)
        # FIXME: copytree is kind of scary. Eventually would like to replace
        # this with a NotImplementedError in order to force explicit creates
        # and file copies
        elif isinstance(src_elem, Dir):
            shutil.copytree(src, dst, symlinks=True)
        elif isinstance(src_elem, Link):
            os.symlink(os.readlink(src), dst)
        else:  # pragma: no cover
            assert False
