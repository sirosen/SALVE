#!/usr/bin/python

import abc
import os
from contextlib import contextmanager


class AbstractFileOrDir(object):
    """
    This is an abstraction layer to make interactions with a real and mocked
    files and directories uniform. Implementation should not know when it is
    operating on a mock filesystem vs. a real one.

    There are common properties to files and directories that must be defined,
    this abstract class that specifies those properties.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, path):
        self.path = path

    @abc.abstractmethod
    def access(self, mode, *args, **kwargs):  # pragma: no cover
        """
        Preform an access check as with os.access, returning True or False
        depending on the type of access available.

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
        pass

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
        pass


class AbstractFile(AbstractFileOrDir):
    """
    This is an abstraction layer to make interactions with a real and mocked
    files uniform. The implementation of actions, loggers, and other
    file modifiers should be able to pass through this layer transparently when
    the underlying files are real, but have no knowledge that they are not
    operating on a real filesystem when the files are in-memory mocks.
    """
    __metaclass__ = abc.ABCMeta

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
        pass


class AbstractDir(AbstractFileOrDir):
    """
    This is an abstraction layer to make interactions with a real and mocked
    directories uniform. Client code using subclasses of this should be able to
    write ambiguously, not knowing if they operate on a real or mocked
    filesystem.
    """
    __metaclass__ = abc.ABCMeta

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
        pass
