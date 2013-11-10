#!/usr/bin/python

# This is a library of small functions and variables designed to make
# it easy for components of SALVE to refer to the SALVE root directory,
# and any globally important directories like the metadata directory
# and the file cache

import os

def containing_dir(path):
    return os.path.dirname(os.path.abspath(path))

def get_salve_root():
    return containing_dir(containing_dir(containing_dir(__file__)))

def get_default_config():
    return os.path.join(get_salve_root(),'default_settings.ini')