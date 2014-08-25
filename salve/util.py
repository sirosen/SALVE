#!/usr/bin/python

import os
import hashlib
import copy


class Enum(object):
    def __init__(self, *seq, **named):
        """
        Usually, enum values are strings, so we map them to themselves
        for tidy output. For example

        >>> x = Enum('A','B')
        >>> print(x.A) # "A"
        >>> x.B == 'B' # True

        This should not be relied on in code for tests and control
        statements because the enum may be given explicitly named attrs
        like

        >>> x = Enum('A','B',C='x.C',D='Enum(x).D')

        in which case

        >>> print(x.C) # "x.C"
        >>> print(x.D) # "Enum(x).D"

        Instead, enums should be used in the traditional way for tests:

        >>> y = x.C
        >>> ...
        >>> if y == x.C:
        >>>     ...

        or

        >>> if y is x.C:
        >>>     ...

        is tests should pass because y is just another ref to the same
        string.

        Args:
            @seq
            A list of string arguments to be added as attributes mapped
            to themselves as values.

        KWArgs:
            @named
            A set of attribute-value mappings to be mapped into the
            enum.
        """
        self.enum_elems = {}
        self.add(*seq, **named)

    def __contains__(self, x):
        """
        Checks if @x is in an enum. Defines the results of 'in' tests.
        """
        return x in self.enum_elems

    def __iter__(self):
        """
        An iterator over the enum, yields the keys of the enum, rather than the
        values.
        """
        for x in self.enum_elems:
            yield x

    def add(self, *seq, **named):
        """
        Adds elements to the enum.
        """
        enums = dict([(x, x) for x in seq], **named)
        self.__dict__.update(enums)
        self.enum_elems.update(enums)

    def extend(self, *seq, **named):
        """
        Creates a new enum with @seq and @named added.
        """
        new = copy.copy(self)
        new.add(*seq, **named)
        return new


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


"""
Ported functionality from the Python2/Python3 compatibility library, six

The code below is provided under the license and copyright of the six
project:

Copyright (c) 2010-2014 Benjamin Peterson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})
