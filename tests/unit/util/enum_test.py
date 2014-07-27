#!/usr/bin/python

from nose.tools import istest

import salve.util.enum as enum


@istest
def automapping():
    """
    Unit: Enum Util Automapping
    Tests that the automatic mapping of strings in an enum
    correctly assigns them to themselves.
    """
    x = enum.Enum('A', 'B')
    y = x.B
    assert(x.A == 'A')
    assert(x.B is y)


@istest
def explicit_mapping():
    """
    Unit: Enum Util Explicit Mapping
    Tests that the explicit mapping of attrs in an enum using kwargs
    results in those kwargs being correctly assigned.
    """
    def func():
        pass
    x = enum.Enum(A=1, B='x.B', C=func)
    assert(x.A == 1)
    assert(x.B == 'x.B')
    assert(x.C is func)


@istest
def mixed_mapping():
    """
    Unit: Enum Util Mixed Mapping
    Tests that a mixture of automatic and explicit assignments has the
    desired effect.
    """
    def func():
        pass
    x = enum.Enum('A', B='x.B', C=func)
    assert(x.A == 'A')
    assert(x.B == 'x.B')
    assert(x.C is func)
