#!/usr/bin/python

def get_filename(stream):
    """
    Gets the filename for a given IO stream if it exists.
    """
    fname = None
    if hasattr(stream,'name'):
        fname = stream.name
    return fname
