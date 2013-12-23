#!/usr/bin/python

import grp, pwd, os

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
