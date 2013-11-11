#!/usr/bin/python

import src.util.enum as enum
from nose.tools import istest

@istest
def automapping():
    x = enum.Enum('A','B')
    y = x.B
    assert(x.A == 'A')
    assert(x.B is y)

@istest
def explicit_mapping():
    def func(): pass
    x = enum.Enum(A=1,B='x.B',C=func)
    assert(x.A == 1)
    assert(x.B == 'x.B')
    assert(x.C is func)

@istest
def mixed_mapping():
    def func(): pass
    x = enum.Enum('A',B='x.B',C=func)
    assert(x.A == 'A')
    assert(x.B == 'x.B')
    assert(x.C is func)
