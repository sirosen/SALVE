#!/usr/bin/python

# This is a library of small functions and variables designed to make
# it easy for components of SALVE to refer to the SALVE root directory,
# and any globally important directories like the metadata directory
# and the file cache

import os

def containing_dir(path,depth=1):
    d = os.path.abspath(path)
    for i in xrange(depth):
        d = os.path.dirname(d)
    return d

def get_salve_root():
    return containing_dir(__file__,depth=3)

def get_default_config():
    return os.path.join(get_salve_root(),'default_settings.ini')
