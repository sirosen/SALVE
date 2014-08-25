#!/usr/bin/python

import os
import timeit
from nose.tools import istest

from tests.util import full_path

import salve.util


@istest
def stream_filename():
    """
    Unit: Util Get Stream Filename
    Tests stream_filename on real files, given the File objects.
    """
    for char in ['a', 'b', 'c']:
        name = full_path(char)
        with open(name) as f:
            assert salve.util.stream_filename(f) == name


@istest
def sha512_empty_match():
    """
    Unit: Streams Util SHA512 Empty File Match
    Ensures that the sha512 hashes of two empty files match.
    """
    aname = full_path('a')
    bname = full_path('b')
    ahash, bhash = None, None
    with open(aname) as f:
        ahash = salve.util.sha512(f)
    with open(bname) as f:
        bhash = salve.util.sha512(f)
    assert ahash == bhash


@istest
def sha512_nonempty_match():
    """
    Unit: Streams Util SHA512 Non-Empty File Match
    Ensures that the sha512 hashes of two nonempty files match.
    """
    cname = full_path('c')
    dname = full_path('d')
    ahash, chash = None, None
    with open(cname) as f:
        chash = salve.util.sha512(f)
    with open(dname) as f:
        dhash = salve.util.sha512(f)
    assert chash == dhash


@istest
def sha512_mismatch():
    """
    Unit: Streams Util SHA512 File Mismatch
    Ensures that the sha512 hashes of nonmatching files don't match.
    """
    aname = full_path('a')
    cname = full_path('c')
    ahash, chash = None, None
    with open(aname) as f:
        ahash = salve.util.sha512(f)
    with open(cname) as f:
        chash = salve.util.sha512(f)
    assert ahash != chash
