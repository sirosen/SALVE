#!/usr/bin/python

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
