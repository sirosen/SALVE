#!/usr/bin/python

"""
This is a library of small functions and variables designed to make
it easy for components of SALVE to refer to the SALVE root directory,
and any globally important directories like the metadata directory
and the file cache
"""

import os
import re


def containing_dir(path, depth=1):
    """
    Gets a specific ancestor of a directory.

    Args:
        @path
        The directory whose ancestor should be returned.

    KWArgs:
        @depth
        The number of directories up the tree to look.
    """
    d = os.path.abspath(path)
    for i in range(depth):
        d = os.path.dirname(d)
    return d


def get_default_config():
    """
    Get the location of the default settings ini file.
    """
    return os.path.abspath(
            os.path.join(containing_dir(__file__),
                '../default_settings.ini'))


def is_abs_or_var(path):
    """
    Checks if a path is absolute, or begins with a variable.
    Useful to check if more expansion of one kind or another is needed.

    Args:
        @path
        The string to check for being an absolute or variable path.
    """
    if os.path.isabs(path):
        return True
    # matches: [begin string][even number of $][$][end string or non-$]
    if re.match('^(\\$\\$)*\\$([^$]|$)', path):
        return True

    return False


def clean_path(path, absolute=False):
    """
    Cleans up a path for printing or logging. Primarily, this is
    just and invocation of os.path.normpath, but it may also alter
    the path to relative or absolute.

    Args:
        @path
        The path that will be altered and returned.

    KWArgs:
        @absolute
        Convert the path to absolute? When false, taken to mean that
        the path should be converted to relative with respect to the
        cwd.
    """
    if absolute:
        path = os.path.abspath(path)
    else:
        # use a relative path if it is shorter
        rpath = os.path.relpath(path, '.')
        if len(rpath) < len(path):
            path = rpath

    return os.path.normpath(path)


def pjoin(*args, **kwargs):
    """
    Lightweight wrapper around os.path.join

    Serves only to abstract away from the os module
    """
    return os.path.join(*args, **kwargs)


def dirname(*args, **kwargs):
    """
    Lightweight wrapper around os.path.dirname

    Serves only to abstract away from the os module
    """
    return os.path.dirname(*args, **kwargs)
