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
    # abspath makes it absolute and normpath
    # normalizes things like '/a/../b' to '/b'
    # don't normalize symlinks because those may conflict with entries in the
    # virtual FS
    return os.path.normpath(os.path.abspath(path))


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
            """
            A helper that does the actual normalization work. Needed because
            the final product goes through a mild amount of post-processing.

            Args:
                @path
                The path whose links (virtual and real) need to be
                dereferenced.

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
        path = self._normalize_virtual_links(normalize_path(path))
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
