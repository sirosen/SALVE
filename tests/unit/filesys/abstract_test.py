#!/usr/bin/python

from nose.tools import istest
from tests.utils.exceptions import ensure_except

from salve.filesys import abstract


@istest
def filesys_is_abstract():
    """
    Unit: Filesys Base Class Is Abstract
    Ensures that a Filesys cannot be instantiated.
    """
    ensure_except(TypeError, abstract.Filesys)
