#!/usr/bin/python

import os
import hashlib


def stream_filename(stream):
    """
    Gets the filename for a given IO stream if it exists.

    Args:
        @stream
        A file like object whose name is desired.
    """
    fname = None
    if hasattr(stream, 'name'):
        fname = stream.name
    return fname


def sha512(stream):
    """
    Computes the sha512 hash of the contents of the stream.

    Args:
        @stream
        A file like object whose sha512 has is desired.
    """
    hash = hashlib.sha512()
    while True:
        string = stream.read(2 ** 20).encode('utf-8')
        if string:
            hash.update(string)
        else:
            return hash.hexdigest()


def hash_from_path(path):
    if os.path.islink(path):
        link_contents = os.readlink(path).encode('utf-8')
        return hashlib.sha256(link_contents).hexdigest()
    else:
        with open(path) as f:
            return sha512(f)
