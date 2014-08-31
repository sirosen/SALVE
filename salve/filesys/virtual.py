#!/usr/bin/python

import os
import shutil
import abc
from contextlib import contextmanager

from salve.filesys import abstract
from salve.util import with_metaclass
from salve.paths import dirname, pjoin


def normalize_path(path):
    """
    Normalize a path per the standards of the virtual filesystem.
    This is slightly more extensive than any particular component of the
    os.path module.
    """
    # abspath makes it absolute, realpath removes symlinks, and normpath
    # normalizes things like '/a/../b' to '/b'
    return os.path.normpath(os.path.realpath(os.path.abspath(path)))


class VirtualFSElement(with_metaclass(abc.ABCMeta)):
    def __init__(self, path):
        # create a new fs element
        self.path = normalize_path(path)

        # set basic properties (to defaults)
        # existence
        self.exists = False
        # stat properties
        self.uid = None
        self.gid = None
        self.mode = None
        self.nlink = None
        self.ino = None
        self.size = 0
        self.atime = None
        self.mtime = None
        self.ctime = None


class VirtualFile(VirtualFSElement):
    def __init__(self, path):
        VirtualFSElement.__init__(self, path)
        self.content = None

    def check_access(self, access_flags):
        return False


class VirtualDir(VirtualFSElement):
    def check_access(self, access_flags):
        return False


class VirtualLink(VirtualFSElement):
    def __init__(self, path):
        VirtualFSElement.__init__(self, path)
        self.link_target = None

    def check_access(self, access_flags):
        return False


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
        loop_detector = {}

        def normalize_vlinks_helper(path):
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

            # if there is a registered FS element, check its type
            # and if it is a link, follow it
            if self._has(reformed_path):
                if self.lookup_type(reformed_path) != self.element_types.LINK:
                    return reformed_path
                else:
                    elem = self._lookup(reformed_path)

                    # if the symlink is absolute, restart normalization
                    if os.path.isabs(elem.link_target):
                        return normalize_vlinks_helper(elem.link_target)

                    else:
                        # normpath is safe because it doesn't look at symlinks
                        # and such on the real FS (which could conflict with
                        # the virtual symlinks)
                        new_path = os.path.normpath(pjoin(head,
                            elem.link_target))

                        # record link remappings so as to catch loops
                        loop_detector[reformed_path] = new_path

                        # if we are chasing two symlinks which point at one
                        # another, do like realpath and return the former one
                        # (still have to normalize its ancestors)
                        if new_path in loop_detector:
                            return new_path
                        else:
                            return normalize_vlinks_helper(pjoin(head,
                                elem.link_target))

            # if we're looking at a filesys symlink without an entry in the
            # lookup table, we have no worries unless an ancestor of this is a
            # virtual link that leads us elsewhere, but that can't be the case
            # for the reformed path because we already normalized ancestors
            elif os.path.islink(reformed_path):
                return normalize_vlinks_helper(os.path.realpath(reformed_path))

            # otherwise, just look for symlinks in the ancestry
            return reformed_path

        return normalize_path(normalize_vlinks_helper(path))

    def lookup_type(self, path):
        """
        Lookup the type of a given path.
        Fails over onto the real filesystem if there is no registered element
        at a location.

        Args:
            @path
            The path to the file, dir, or link to lookup.
        """
        # if there is a matching element, check its class
        if path in lookup_table:
            elem = self.lookup_table[path]
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

        ###
        # FIXME: ignores the handling of VirtualLinks that may appear in the
        # path -- these need to be resolved as part of the path cleaning
        # process
        ###

        path = normalize_path(path)
        parent = dirname(path)

        if not self.exists(path):
            if recursive:
                elem = VirtualDir(path)
                self._register(elem)
                self.mkdir(parent, recursive=True)
            else:
                if self.exists(parent):
                    elem = VirtualDir(path)
                    self._register(elem)
                else:
                    return OSError(2,
                            "No such file or directory: '%s'" % path)
