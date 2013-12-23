#!/usr/bin/python

import os
import timeit
from nose.tools import istest

import src.util.streams

_testfile_dir = os.path.join(os.path.dirname(__file__),'files')

@istest
def get_filename():
    """
    Streams Util Get Stream Filename
    Tests get_filename on real files, given the File objects.
    """
    for char in ['a', 'b', 'c']:
        name = os.path.join(_testfile_dir,char)
        with open(name) as f:
            assert src.util.streams.get_filename(f) == name

@istest
def sha512_empty_match():
    """
    Streams Util SHA512 Empty File Match
    Ensures that the sha512 hashes of two empty files match.
    """
    aname = os.path.join(_testfile_dir,'a')
    bname = os.path.join(_testfile_dir,'b')
    ahash,bhash = None,None
    with open(aname) as f:
        ahash = src.util.streams.sha_512(f)
    with open(bname) as f:
        bhash = src.util.streams.sha_512(f)
    assert ahash == bhash

@istest
def sha512_nonempty_match():
    """
    Streams Util SHA512 Non-Empty File Match
    Ensures that the sha512 hashes of two nonempty files match.
    """
    cname = os.path.join(_testfile_dir,'c')
    dname = os.path.join(_testfile_dir,'d')
    ahash,chash = None,None
    with open(cname) as f:
        chash = src.util.streams.sha_512(f)
    with open(dname) as f:
        dhash = src.util.streams.sha_512(f)
    assert chash == dhash

@istest
def sha512_mismatch():
    """
    Streams Util SHA512 File Mismatch
    Ensures that the sha512 hashes of nonmatching files don't match.
    """
    aname = os.path.join(_testfile_dir,'a')
    cname = os.path.join(_testfile_dir,'c')
    ahash,chash = None,None
    with open(aname) as f:
        ahash = src.util.streams.sha_512(f)
    with open(cname) as f:
        chash = src.util.streams.sha_512(f)
    assert ahash != chash

@istest
def sha512_hash_is_fast():
    """
    Streams Util SHA512 Is Fast
    Tests that sha512 hashes are taken fast enough. This is not a
    serious performance test, but rather insurance against extra work
    being introduced into the hashing function.
    """
    cname = os.path.join(_testfile_dir,'c')
    t = timeit.timeit(
            'with open("'+cname+'") as f: src.util.streams.sha_512(f)',
            setup='import src.util.streams',number=1000
        )
    # this has a wide margin of error (one order of magnitude) and
    # should therefore pass even on systems with relatively high load
    # on _very_ old systems this test might fail, but it just ensures
    # that our hashing method is acceptably fast
    assert t < 0.5
