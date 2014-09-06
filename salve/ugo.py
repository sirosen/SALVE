#!/usr/bin/python

import os
import grp
import pwd


def get_group_from_username(username):
    """
    Gets the primary group of a user based on NIS.

    Args:
        @username
        The user whose primary group should be fetched.
    """
    return grp.getgrgid(pwd.getpwnam(username).pw_gid).gr_name


def is_root():
    """
    Checks if the process is running as root.
    """
    return os.geteuid() == 0


def name_to_uid(username):
    """
    Gets the UID for a user, based on NIS.

    Args:
        @username
        The user whose UID is desired.
    """
    return pwd.getpwnam(username).pw_uid


def name_to_gid(groupname):
    """
    Gets the GID for a group, based on NIS.

    Args:
        @groupname
        The group whose GID is desired.
    """
    return grp.getgrnam(groupname).gr_gid


def is_owner(path):
    """
    Checks if the current user owns a file.

    Args:
        @path
        Path to the file whose ownership is being checked.
    """
    # the operation is only allowed on existing files
    assert os.path.exists(path)

    return os.stat(path).st_uid == os.geteuid()


def get_current_umask():
    """
    Gets and returns the current umask as an octal integer. Does not modify the
    umask (although this is not threadsafe, as it will have to modify it
    temporarily in order to get it).
    """
    # doesn't matter what we set it to here. 000 is the most conservative
    # choice (cannot cause bugs that expose data unnecessarily)
    old_mask = os.umask(0o000)
    os.umask(old_mask)
    return old_mask
