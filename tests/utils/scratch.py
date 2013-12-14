#!/usr/bin/python

import os, tempfile, shutil

def make_scratch(obj):
    obj.scratch_dir = tempfile.mkdtemp()

def rm_scratch(obj):
    shutil.rmtree(obj.scratch_dir)

def make_scratchdir(obj,relpath):
    full_path = os.path.join(obj.scratch_dir,relpath)
    if not os.path.exists(full_path):
        os.makedirs(full_path)

def write_scratchfile(obj,relpath,content):
    with open(os.path.join(obj.scratch_dir,relpath),'w') as f:
        f.write(content)

def read_scratchfile(obj,relpath):
    with open(os.path.join(obj.scratch_dir,relpath),'r') as f:
        return f.read()

def get_scratchfile_mode(obj,relpath):
    return os.stat(os.path.join(obj.scratch_dir,relpath)).st_mode\
           & 0777

