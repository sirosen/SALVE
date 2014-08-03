#!/usr/bin/python

from salve.filesys.abstract import FilesysElement
from salve.filesys.abstract import File
from salve.filesys.abstract import Dir
from salve.filesys.abstract import Link
from salve.filesys.abstract import Filesys

from salve.filesys.concrete import FilesysElement as ConcreteFilesysElement
from salve.filesys.concrete import File as ConcreteFile
from salve.filesys.concrete import Dir as ConcreteDir
from salve.filesys.concrete import Link as ConcreteLink
from salve.filesys.concrete import Filesys as ConcreteFilesys

real_fs = ConcreteFilesys()
