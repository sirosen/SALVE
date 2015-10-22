from nose.tools import istest

from tests.util import full_path

import salve.util


def compare_shas(f1, f2):
    with open(full_path(f1)) as f:
        f1hash = salve.util.sha512(f)
    with open(full_path(f2)) as f:
        f2hash = salve.util.sha512(f)
    return f1hash == f2hash


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
    assert compare_shas('a', 'b')


@istest
def sha512_nonempty_match():
    """
    Unit: Streams Util SHA512 Non-Empty File Match
    Ensures that the sha512 hashes of two nonempty files match.
    """
    assert compare_shas('c', 'd')


@istest
def sha512_mismatch():
    """
    Unit: Streams Util SHA512 File Mismatch
    Ensures that the sha512 hashes of nonmatching files don't match.
    """
    assert not compare_shas('a', 'c')
