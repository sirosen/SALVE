#!/usr/bin/python

from salve.filesys.abstract import Filesys

from salve.filesys.concrete import Filesys as ConcreteFilesys

real_fs = ConcreteFilesys()
