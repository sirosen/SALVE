#!/usr/bin/python

import os

from salve.util import Enum
from salve.filesys.abstract import Filesys
from salve.filesys.concrete import Filesys as ConcreteFilesys

# this is really just an alias to let us get the "os" module entirely out of
# the picture in many parts of the codebase
access_codes = Enum(R_OK=os.R_OK, W_OK=os.W_OK, X_OK=os.X_OK, F_OK=os.F_OK)


real_fs = ConcreteFilesys()
