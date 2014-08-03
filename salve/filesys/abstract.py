#!/usr/bin/python

import abc
import os
from contextlib import contextmanager

from salve.util.six import with_metaclass


class FilesysElement(with_metaclass(abc.ABCMeta)):
    """
    This is an abstraction layer to make interactions with a real and mocked
    files and directories uniform. Implementation should not know when it is
    operating on a mock filesystem vs. a real one.

    There are common properties to files and directories that must be defined,
    this abstract class that specifies those properties.
    """
    def __init__(self, path):  # pragma: no cover
        """
        Although typically an abstract class has no initializer specified, this
        one is being used to clarify that the initializer for a FilesysElement
        must assign a value to self.path, since that is the main data being
        held in the FilesysElement.
        """
        self.path = path

    def __str__(self):
        """
        A string representation of a filesys element is just its path.
        """
        return self.path

    def parent_path(self):
        """
        Every FilesysElement has a parent directory in its path structure.
        The only exception is '/' which has itself as a parent, but this is
        already handled by os.path.dirname, so this is just a transparent call
        to dirname on the underlying path.
        """
        return os.path.dirname(self.path)

    @abc.abstractmethod
    def create(self, *args, **kwargs):  # pragma: no cover
        """
        Create the element, could be any of the various element types. Note
        that creation may require additional arguments or additional
        specifications given by object attributes.
        This is an agnostic version of the underlying mkdir, symlink, and touch
        methods of the File, Dir, and Link types.
        """

    @abc.abstractmethod
    def access(self, mode, *args, **kwargs):  # pragma: no cover
        """
        Preform an access check as with os.access, returning True or False
        depending on the type of access available.
        Follows symlinks, assuming (as on Linux platforms) that symlink
        permissions are those of the destination.

        Args:
            @mode
            As per os.access, this must either be
                os.F_OK
            or an inclusive OR of
                os.W_OK
                os.R_OK
                os.X_OK
            When operating on a real file, arguments are presumably passed
            transparently through to the os.access() function
        """

    @abc.abstractmethod
    def stat(self, *args, **kwargs):  # pragma: no cover
        """
        Get the results of a stat on the file or directory, raising an OSError
        (errno=2, no such file or directory) if it does not exist. Only
        guaranteed to return an object, of an unspecified type, with the
        attributes
            st_mode - protection bits
            st_ino - inode number
            st_nlink - number of hard links
            st_uid - user id of owner
            st_gid - group id of owner
            st_size - size of file, in bytes
            st_atime - time of most recent access
            st_mtime - time of most recent content modification
            st_ctime - time of most recent metadata change

        Does not follow symlinks, so on real filesystem access, this is the
        equivalent of doing

        >>> os.lstat(self.path)

        but it is not safe to assume that nothing else happens. There may be
        other processing at play. In other words, don't call os.lstat on the
        underlying file and expect the same things to happen.
        """

    @abc.abstractmethod
    def chmod(self, mode, *args, **kwargs):  # pragma: no cover
        """
        Chmods the file or directory to a given mode, in the form of an octal
        int. Follows symlinks.

        On real files and directories, should behave like

        >>> os.chmod(self.path)

        Args:
            @mode
            An octal int for ugo-style permissions, as in 0o777 or 0o644
        """

    @abc.abstractmethod
    def chown(self, uid, gid, *args, **kwargs):  # pragma: no cover
        """
        Chowns the file or directory to a given user in the form of a uid and a
        given group in the form of a gid. Does not follow symlinks.

        On real files and directories, should behave like

        >>> os.lchown(self.path, uid, gid)

        If one of the values is not changing, this can be handled through a
        stat() call, a la

        >>> self.chown(new_uid, self.stat().st_gid)

        or

        >>> self.chown(self.stat().st_uid, new_gid)

        Args:
            @uid
            The integer uid to set on the file or directory.

            @gid
            The integer gid to set on the file or directory.
        """

    @abc.abstractmethod
    def exists(self, *args, **kwargs):  # pragma: no cover
        """
        Returns true if the file/dir exists, and false if it does not.

        This is meaningful in general, as creating an abstract file or
        directory to refer to a location does not necessarily indicate that any
        file or directory creation has taken place. That would require an
        explicit creation action, which in the case of a virtualized filesys
        means (more or less) flipping a boolean flag, and in the case of a real
        filesystem means applying a mkdir or touch operation.

        Does not follow symlinks, so this is not equivalent to an invocation of

        >>> self.access(os.F_OK)

        but instead will behave much like

        >>> os.lexists(self.path)

        in which broken symlinks still appear as "present"
        """

    @abc.abstractmethod
    def hash(self, *args, **kwargs):  # pragma: no cover
        """
        Get a hash of the contents of the FilesysElement.
        Generally used for quick comparison of files and symlinks, much like a
        symbol table for fast string comparisons. This will be a sha512 hash of
        any files, and a sha256 hash of any symlinks' paths (not the contents
        of the linked file).
        The hash() operation has no significance on directories, and its
        behavior on them is undefined.
        """


class File(with_metaclass(abc.ABCMeta, FilesysElement)):
    """
    This is an abstraction layer to make interactions with a real and mocked
    files uniform. The implementation of actions, loggers, and other
    file modifiers should be able to pass through this layer transparently when
    the underlying files are real, but have no knowledge that they are not
    operating on a real filesystem when the files are in-memory mocks.
    """
    @abc.abstractmethod
    @contextmanager
    def open(self, *args, **kwargs):  # pragma: no cover
        """
        Open the file, returning a file-like object for interaction. Since this
        method itself is a contextmanager, it must follow the contextlib
        __enter__, yield, __exit__ paradigm. It can be used to wrap existing
        contextmanagers like so:

        >>> def open(self, mode):
        >>>     enter()
        >>>     with open(self.path, *args, **kwargs) as f:
        >>>         yield f
        >>>     exit()
        """

    @abc.abstractmethod
    def touch(self, *args, **kwargs):  # pragma: no cover
        """
        Create the file, using the default system umask (whatever it is) and
        the current euid and egid values. Doesn't do any fancy logic about
        chmoding or chowning the file after creation -- simply brings it into
        the world in whatever state is sensible.
        """

    def create(self, *args, **kwargs):
        """
        Pass through to touch()
        """
        self.touch(*args, **kwargs)


class Link(with_metaclass(abc.ABCMeta, FilesysElement)):
    """
    This is an abstraction layer to make interactions with a real and mocked
    symlinks uniform.
    """
    @abc.abstractmethod
    def symlink(self, path, *args, **kwargs):  # pragma: no cover
        """
        Creates a symlink at self.path to @path

        Like File.touch(), this does not do any special logic on
        ownership &c, but simply creates the symlink with whatever settings are
        applied by the current effective uid and gid.

        Args:
            @path
            The destination path to which the symlink points
        """

    def create(self, *args, **kwargs):
        """
        Pass through to symlink()
        """
        self.symlink(*args, **kwargs)


class Dir(with_metaclass(abc.ABCMeta, FilesysElement)):
    """
    This is an abstraction layer to make interactions with a real and mocked
    directories uniform. Client code using subclasses of this should be able to
    write ambiguously, not knowing if they operate on a real or mocked
    filesystem.
    """
    @abc.abstractmethod
    def walk(self, *args, **kwargs):  # pragma: no cover
        """
        An iterator over the contents of the directory, yielding 3-tuples of
        the form

        (dirname, subdirs, files)

        where dirname is the path to the directory rooted at self.path, subdirs
        is a list of subdirectory names (which will be included in later
        iterations), and files is a list of file names found inside of the
        directory at dirname.

        If the directory does not exist, the iterator is empty, as opposed to a
        single iteration with (name, [], []), as would be given if it were an
        existing empty directory.
        """

    @abc.abstractmethod
    def mkdir(self, recursive=True, *args, **kwargs):  # pragma: no cover
        """
        Create the directory. Behaves very much like File.touch(),
        using the current umask and not performing any special logic on the
        resulting directory.

        KWArgs:
            @recursive=True
            When true, create all parent directories necessary for a directory
            to exist. When false, if an ancestor directory does not exist, an
            OSError will be thrown.
        """

    def create(self, *args, **kwargs):
        """
        Pass through to mkdir()
        """
        self.mkdir(*args, **kwargs)


class Filesys(with_metaclass(abc.ABCMeta)):
    """
    This defines the properties of the filesystem layer, through which
    interactions with the underlying files and directories take place. This
    includes fetching the FilesysElement objects that represent the
    files/directories at certain paths.
    """
    @abc.abstractmethod
    def register(self, elem, *args, **kwargs):  # pragma: no cover
        """
        Registers a FilesysElement in the Filesys representation. Future
        lookups for the element's path will return the registered element. May
        override an existing registered element.

        Args:
            @elem
            The filesys element to register, using @elem.path
        """

    @abc.abstractmethod
    def lookup(self, path, elem_type=None,
            *args, **kwargs):  # pragma: no cover
        """
        Return the FilesysElement registered to @path. May implicitly create an
        element to return, if able.
        Returns None if there is no element for the path and one cannot be
        created.
        Note that the FilesysElement for a given path is fixed, and multiple
        invocations will return refs to the same underlying object.

        Args:
            @path
            The path to the file, directory, or symlink to inspect.

            @elem_type
            A type used for FilesysElement construction in the event that the
            lookup fails. This is used if there is no registered element and
            the lookup still wants to succeed.
            If the type is abstract, it is up to the discretion of the concrete
            class to determine which constructor to call. For example, if a
            salve.filesys.abstract.File is given, it suggests to the concrete
            lookup implementation that a file is desired.
        """

    @abc.abstractmethod
    def copy(self, src, dst, *args, **kwargs):  # pragma: no cover
        """
        Copies a file or directory (recursive) from the source to the
        destination, given as paths.

        Args:
            @src
            The source file, as a path.

            @dst
            The destination file, as a path.
        """
