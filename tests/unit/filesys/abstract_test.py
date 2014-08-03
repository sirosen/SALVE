#!/usr/bin/python

from nose.tools import istest
from tests.utils.exceptions import ensure_except

from salve.filesys import abstract


@istest
def filesyselement_is_abstract():
    """
    Unit: Filesys FilesysElement Base Class Is Abstract
    Ensures that a FilesysElement cannot be instantiated.
    """
    ensure_except(TypeError, abstract.FilesysElement, '/dummy/path')


@istest
def file_is_abstract():
    """
    Unit: Filesys File Base Class Is Abstract
    Ensures that a File cannot be instantiated.
    """
    ensure_except(TypeError, abstract.File, '/dummy/path')


@istest
def link_is_abstract():
    """
    Unit: Filesys Link Base Class Is Abstract
    Ensures that a Link cannot be instantiated.
    """
    ensure_except(TypeError, abstract.Link, '/dummy/path')


@istest
def dir_is_abstract():
    """
    Unit: Filesys Dir Base Class Is Abstract
    Ensures that a Dir cannot be instantiated.
    """
    ensure_except(TypeError, abstract.Dir, '/dummy/path')


@istest
def filesys_is_abstract():
    """
    Unit: Filesys Base Class Is Abstract
    Ensures that a Filesys cannot be instantiated.
    """
    ensure_except(TypeError, abstract.Filesys)
