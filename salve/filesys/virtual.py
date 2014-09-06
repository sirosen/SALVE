#!/usr/bin/python

import os
import time
import shutil
import abc
from contextlib import contextmanager
from collections import namedtuple

from salve.filesys import abstract
from salve.util import with_metaclass
from salve.ugo import get_current_umask
from salve.paths import dirname, pjoin


# Stat information is a named tuple (lighter weight than a full class just for
# these attributes)
StatInfo = namedtuple('StatInfo', 'st_uid', 'st_gid', 'st_mode',
        'st_nlink', 'st_ino', 'st_size', 'st_atime', 'st_mtime',
        'st_ctime')


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
        self.path = filesys._normalize_virtual_links(path)

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

    def _has(self, path):
        return path in self.lookup_table

    def _lookup(self, path):
        return self.lookup_table[path]

    def _normalize_virtual_links(self, path):
        """
        Walks a path, rewriting all virtual links as though applying readlink
        to them. Then does a pass of normalization for safety.
        """
        path = os.path.abspath(path)
        loop_detector = {}

        def normalize_vlinks_helper(path):
            """
            A helper that does the actual normalization work. Needed because
            the final product goes through a mild amount of post-processing.

            Args:
                @path
                The path whose links (virtual and real) need to be expanded.

            Technique is, in short, to handle the path recursively.
            First, normalize all real and virtual links in the dirname, then
            look at the dirname joined with the basename.
            If the result does not exists (according to the virtual FS), then
            it is a broken symlink, and is returned as-is.
            Next, it is inspected to see if it is a symlink or not. If not, the
            work is done and the path can be returned. Symlinks are checked for
            being absolute or relative. Absolute links restart the
            normalization process, while relative ones are joined to the
            dirname, subject to some basic normalization (os.path.normpath),
            and restart normalization.

            Importantly, many results are memoized. This is not just a
            performance measure, but also ensures that symlink loops are
            detected and produce a meaningful result. As an unfortunate
            side-effect, loops produce the target of the original link as their
            result, not the path to the original link (a slight deviation from
            os.path.realpath). Fixing this is a low-priority item.
            """
            (head, tail) = os.path.split(path)
            # check to see if we've reached the root
            # recursive base case
            if tail == "":
                return path

            normed_prefix = normalize_vlinks_helper(head)
            reformed_path = pjoin(normed_prefix, tail)

            # if the directory does not exist in the virtual FS, then a
            # symlink is broken, but should be returned verbatim
            if not self.exists(normed_prefix):
                return reformed_path

            # if this path refers to a real or virtual symlink that we've seen
            # in the past, then return whatever it dereferenced to -- prevents
            # loops and potentially saves us from recomputing

            # notably, does not cause problems with structures like
            # /a/b -> /a/c  and  /a -> /p/q/r/
            # in which we will read '/a/b' and produce '/p/q/r/b'
            # after which we will get '/a/c' and be forced to handle '/a' again
            if reformed_path in loop_detector:
                return loop_detector[reformed_path]

            # if there is a registered FS element, check its type
            # and if it is a link, follow it
            if self._has(reformed_path):
                if self.lookup_type(reformed_path) != self.element_types.LINK:
                    return reformed_path
                else:
                    elem = self._lookup(reformed_path)
                    new_path = elem.link_target

                    # if the symlink is not absolute, join it with the dir
                    # contianing the reformed path
                    if not os.path.isabs(elem.link_target):
                        # normpath is safe because it doesn't look at symlinks
                        # and such on the real FS (which could conflict with
                        # the virtual symlinks)
                        new_path = os.path.normpath(pjoin(head,
                            elem.link_target))

                    # record link remappings so as to catch loops
                    loop_detector[reformed_path] = new_path

                    return normalize_vlinks_helper(new_path)

            # if we're looking at a filesys symlink without an entry in the
            # lookup table, we have no worries unless an ancestor of this is a
            # virtual link that leads us elsewhere, but that can't be the case
            # for the reformed path because we already normalized ancestors
            elif os.path.islink(reformed_path):
                # read the link, and if it is not absolute, join it with the
                # reformed path's directory
                target = os.readlink(reformed_path)
                if not os.path.isabs(target):
                    target = os.path.normpath(pjoin(head, target))

                # record link remappings so as to catch loops
                loop_detector[reformed_path] = target

                return normalize_vlinks_helper(target)

            # otherwise, take the new path to be the normalized version
            return reformed_path

        return os.path.normpath(normalize_vlinks_helper(path))

    def exists(self, path):
        """
        Check if a file, directory, or link exists at a location in the virtual
        filesystem.

        Args:
            @path
            The path to the file, dir, or link (real or virtual) to check.
        """
        normed_path = self._normalize_virtual_links(path)
        if self._has(normed_path):
            elem = self._lookup(normed_path)
            return elem.exists
        else:
            return self.real_fs.exists(normed_path)

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

    def lookup_type(self, path):
        """
        Lookup the type of a given path.
        Fails over onto the real filesystem if there is no registered element
        at a location.

        Args:
            @path
            The path to the file, dir, or link to lookup.
        """
        path = self._normalize_virtual_links(path)
        # if there is a matching element, check its class
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

        # if no entry matches, inspect the underlying filesystem
        else:
            return self.real_fs.lookup_type(path)

    def mkdir(self, path, recursive=True):
        """
        Create the directory desired, suppressing "already exists" errors.
        May still return OSError(2, 'No such file or directory') when
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
                    return OSError(2,
                            "No such file or directory: '%s'" % path)
