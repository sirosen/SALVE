#!/usr/bin/python

import grp, pwd, os

def get_group_from_username(username):
    return grp.getgrgid(pwd.getpwnam(username).pw_gid).gr_name

def is_root():
    return os.geteuid() == 0

def name_to_uid(username):
    return pwd.getpwnam(username)[2]

def name_to_gid(groupname):
    return grp.getgrnam(groupname)[2]
