#!/usr/bin/python

import grp, pwd, os

def get_group_from_username(username):
    return grp.getgrgid(pwd.getpwnam(username).pw_gid).gr_name

def is_root():
    return os.geteuid() == 0
