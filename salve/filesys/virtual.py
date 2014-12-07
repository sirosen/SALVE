#!/usr/bin/python

import os
import time
import shutil
import abc
from contextlib import contextmanager
from collections import namedtuple

from salve.filesys import abstract
from salve.util import with_metaclass, transitive_dict_resolve
from salve.ugo import get_current_umask
from salve.paths import dirname, pjoin


# Stat information is a named tuple (lighter weight than a full class just for
# these attributes)
StatInfo = namedtuple('StatInfo',
        ('st_uid', 'st_gid', 'st_mode', 'st_nlink', 'st_ino', 'st_size',
         'st_atime', 'st_mtime', 'st_ctime'))


def virtual_inode_number_generator():
    """
    Create dummy unique ids for the virtual inodes. These aren't really used at
    present, but could serve as the basis for hardlinks in the virtual FS.
    """
    c = 1
    while True:
        yield c
        c += 1


def build_new_statinfo(size):
    """
    Build the most generic StatInfo possible, using the currently available
    information. Some basic values are still required from the calling
    function.
    Acts as though it is creating a fresh file, which may or may not be the
    case.
    """
    cur_time = int(time.time())
    return StatInfo(st_uid=os.geteuid(), st_gid=os.getegid(),
            st_mode=get_current_umask(), st_nlink=1,
            st_ino=virtual_inode_number_generator(), st_size=size,
            st_atime=cur_time, st_mtime=cur_time, st_ctime=cur_time)


class VirtualFSElement(with_metaclass(abc.ABCMeta)):
    def __init__(self, filesys, path, stat_info=None):
        """
        Create a new FS element, given a filesystem with which to register it,
        and a path at which the element can be found.
        """
        self.filesys = filesys
        self.path = filesys._normalize_virtual_links(path,
                resolve_last_link=True)

        # set common properties by leveraging the provided stat_info

        # set stat attributes to None if they are not provided
        if stat_info is not None:
            self.stat_info = stat_info
        else:
            self.stat_info = StatInfo(st_uid=None, st_gid=None, st_mode=None,
                    st_nlink=None, st_ino=None, st_size=None,
                    st_atime=None, st_mtime=None, st_ctime=None)

        # existence is determined by checking if there is an inode in the FS
        # element's StatInfo
        self.exists = self.stat_info.st_ino is not None

        # register the new FS element with the filesys
        # safe because __init__ is just an initializer, not a constructor
        filesys._register(self)


class VirtualFile(VirtualFSElement):
    def __init__(self, filesys, path):
        VirtualFSElement.__init__(self, filesys, path)
        self.content = None


class VirtualDir(VirtualFSElement):
    pass


class VirtualLink(VirtualFSElement):
    def __init__(self, filesys, path):
        VirtualFSElement.__init__(self, filesys, path)
        self.link_target = None


class VirtualFilesys(abstract.Filesys):
    def __init__(self):
        # mapping of normalized, link-free paths to elements
        self.lookup_table = {}
        # the underlying real filesys
        self.real_fs = ConcreteFilesys()

    def _register(self, elem):
        self.lookup_table[elem.path] = elem

    """
    Observational functions, do not modify content of the Virtual Filesys.
    These are safe, and independent from functions which may modify Virtual FS
    elements.
    """

    def _has(self, path):
        return path in self.lookup_table

    def _lookup(self, path):
        return self.lookup_table[path]

    def _raw_lookup_type(self, path):
        """
        Lookup the type of a given path.
        Fails over onto the real filesystem if there is no registered element
        at a location. Unlike the public-facing version of this method, does
        not try to do symlink resolution.

        Args:
            @path
            The path to the file, dir, or link to lookup.
        """
        # if it's in the virtual FS, look it up
        if self._has(path):
            elem = self._lookup(path)
            if isinstance(elem, VirtualFile):
                return self.element_types.FILE
            elif isinstance(elem, VirtualDir):
                return self.element_types.DIR
            elif isinstance(elem, VirtualLink):
                return self.element_types.LINK
            else:
                return None
        # if nothing matches, inspect the underlying filesystem
        else:
            return self.real_fs.lookup_type(path)

    def _raw_exists(self, path):
        """
        Check if a file, directory, or link exists at a location in the virtual
        filesystem. Unlike the public-facing version of this method, does not
        try to do symlink resolution.

        Args:
            @path
            The path to the file, dir, or link (real or virtual) to check.
        """
        if self._has(normed_path):
            elem = self._lookup(normed_path)
            return elem.exists
        else:
            return self.real_fs.exists(normed_path)

    def _normalize_virtual_links(self, path, resolve_last_link=False):
        """
        Walks a path, rewriting all virtual links as though applying readlink
        to them. Then does a pass of normalization for safety.

        Args:
            @path
            The path whose links need to be expanded

        KWArgs:
            @resolve_last_link=False
            When false, treat the path as a potential path to a symlink, so
            don't resolve the last element in it. When True, resolve every
            symlink in the path.
        """
        # abspath also does path normalization, so we can now start operating
        # on an absolute path without crazy patterns like '/a/b/.././/./../c'
        path = os.path.abspath(path)
        # the link cache will be used to detect symlink loops, and also to
        # speed up resolution in cases with re-entrant symlink patterns (most
        # commonly a symlink directory in the values of symlinks) that can
        # force reresolution. For example, given
        # /a/b -> /a/c  and  /a -> /p/q/r/
        # we will read '/a/b' and produce '/p/q/r/b' after which we will get
        # '/a/c' and be forced to handle '/a' again
        link_cache = {}

        def normalize_vlinks_helper(path):
            """
            A helper that does the actual normalization work. Needed because
            the final product goes through a mild amount of post-processing.

            Technique is, in short, to handle the path recursively.
            First, normalize all real and virtual links in the dirname, then
            look at the dirname joined with the basename.
            If the result does not exists, then it is a broken symlink.
            If it is not a symlink, we can return it as is.
            Absolute links restart the normalization process, while relative
            ones are joined to the dirname and restart normalization.

            Importantly, many results are memoized. This is not only a
            performance measure, but also ensures that symlink loops are
            detected and produce a meaningful result.

            FIXME: May not always produce results consistent with the behavior
            of os.readlink when handling loops.

            Args:
                @path
                The path whose links (virtual and real) need to be expanded.
            """
            (head, tail) = os.path.split(path)
            # check to see if we've reached the root
            # recursive base case
            if tail == "":
                return path

            # normalize the prefix to this path recursively
            normed_prefix = normalize_vlinks_helper(head)
            reformed_path = pjoin(normed_prefix, tail)

            # if this path refers to a real or virtual symlink that we've seen
            # in the past, then return whatever it dereferences to
            # breaks us out of symlink loops
            if reformed_path in link_cache:
                return transitive_dict_resolve(link_cache, reformed_path)

            # if the location does not exist in the virtual FS, then a
            # symlink is broken, so it should be returned verbatim without any
            # further attempts at resolution
            if not self._raw_exists(reformed_path):
                return reformed_path

            # we now know that we are dealing with a symlink, file, or dir
            # which exists in the virtual FS (this may mean that it is a real
            # symlink in the underlying FS; we don't know yet)
            # the next step is to determine if it is not a link -- in which
            # case we are done -- or to attempt to resolve it if it is one

            # it could be a link in the virtual FS or a link in the real FS
            # a raw lookup is the same as a lookup, but without trying to do
            # symlink normalization before type inspection (infinite recursion
            # badness)
            # it still includes failover to the real FS when elements are
            # absent from the virtual FS
            if self._raw_lookup_type(reformed_path) != self.element_types.LINK:
                return reformed_path

            # now we know it's a link, so we need to do one step of resolution

            # what does our single-step resolution produce?
            # starts as None, but must be set before we're done
            new_path = None

            # if there is a registered virtual FS element, it's a link, so we
            # can start to treat it as such
            if self._has(reformed_path):
                elem = self._lookup(reformed_path)
                new_path = elem.link_target

                # if the symlink is not absolute, join it with the dir
                # containing the reformed path
                if not os.path.isabs(elem.link_target):
                    new_path = pjoin(normed_prefix, elem.link_target)
            # if not a virtual FS element, it must be a real FS symlink
            else:
                # read the link, and if it is not absolute, join it with the
                # reformed path's directory
                new_path = os.readlink(reformed_path)
                if not os.path.isabs(new_path):
                    new_path = pjoin(normed_prefix, new_path)

            # safety assertion so that we blow up if things go sideways
            assert new_path is not None
            # normalize the path to remove icky '/../'-like patterns
            new_path = os.path.normpath(new_path)

            # record link remappings so as to catch loops and short-circuit
            # resolution in the future
            link_cache[reformed_path] = new_path

            return normalize_vlinks_helper(new_path)

        # if the target of resolution is not allowed to be a symlink, then we
        # will follow every link in the path normally
        if resolve_last_link:
            return normalize_vlinks_helper(path)
        # if, on the other hand, we may be normalizing the path to a symlink,
        # then we can only safely operate on the directory component of the
        # path, and not on the final element of it
        # so we have to split the path and join the tail to it after the fact
        else:
            (head, tail) = os.path.split(path)
            return pjoin(normalize_vlinks_helper(head), tail)

    def lookup_type(self, path):
        """
        Lookup the type of a given path.
        Fails over onto the real filesystem if there is no registered element
        at a location.

        Args:
            @path
            The path to the file, dir, or link to lookup.
        """
        # do symlink resolution, but don't follow a link if that's what this
        # resolves to, since we might be doing a type lookup on a symlink
        path = self._normalize_virtual_links(path)
        return self._raw_lookup_type(self, path)

    def exists(self, path):
        """
        Check if a file, directory, or link exists at a location in the virtual
        filesystem.

        Args:
            @path
            The path to the file, dir, or link (real or virtual) to check.
        """
        normed_path = self._normalize_virtual_links(path)
        self._raw_exists(normed_path)

    def stat(self, path):
        """
        Either return the FS element's stat_info (if present), or failover to a
        real filesystem stat.
        """
        normed_path = self._normalize_virtual_links(path)
        if self.exists(normed_path):
            if self._has(normed_path):
                elem = self._lookup(normed_path)
                return elem.stat_info
            else:
                return self.real_fs.stat(normed_path)
        else:
            raise OSError(2, "No such file or directory: '%s'" % path)

    """
    Mutation functions, change content of the Virtual Filesys.
    These depend upon the observational functions, and alter the state of the
    filesystem.
    """

    def _virtualize_file(self, path):
        """
        Virtualize an already existing link, file, or directory.
        """
        # normalize links in the
        normed_path = self._normalize_virtual_links(path)
        if self._has(normed_path):
            return self._lookup(normed_path)

        if not self.exists(normed_path):
            raise OSError(2, "No such file or directory: '%s'" % normed_path)

        ty = self._lookup_type(normed_path)
        if ty is self.element_types.LINK:
            elem = VirtualLink(self, normed_path)
            elem.link_target = os.readlink(normed_path)

    def mkdir(self, path, recursive=True):
        """
        Create the directory desired, suppressing "already exists" errors.
        May still raise OSError(2, 'No such file or directory') when
        nonrecursive mkdir calls have missing ancestors.
        """
        path = self._normalize_virtual_links(path)
        parent = dirname(path)

        if not self.exists(path):
            if recursive:
                elem = VirtualDir(self, path, exists=True)
                self.mkdir(parent, recursive=True)
            else:
                if self.exists(parent):
                    elem = VirtualDir(self, path, exists=True)
                else:
                    raise OSError(2,
                            "No such file or directory: '%s'" % path)
        else:
            existing_ty = self._lookup_type(path)
            if existing_ty is not self.element_types.DIR:
                raise OSError(17, "File exists: '%s'" % path)
