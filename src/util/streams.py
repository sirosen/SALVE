#!/usr/bin/python

import hashlib

def get_filename(stream):
    """
    Gets the filename for a given IO stream if it exists.
    """
    fname = None
    if hasattr(stream,'name'):
        fname = stream.name
    return fname

def sha_512(stream):
    """
    Computes the sha512 hash of the contents of the stream.
    """
    hash = hashlib.sha512()
    while True:
        string = stream.read(2**20)
        if string:
            hash.update(string)
        else:
            return hash.hexdigest()
