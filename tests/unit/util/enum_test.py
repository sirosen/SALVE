from nose.tools import istest

from salve import Enum


@istest
def automapping():
    """
    Unit: Enum Util Automapping
    Tests that the automatic mapping of strings in an enum
    correctly assigns them to themselves.
    """
    x = Enum('A', 'B')
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
    x = Enum(A=1, B='x.B', C=func)
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
    x = Enum('A', B='x.B', C=func)
    assert(x.A == 'A')
    assert(x.B == 'x.B')
    assert(x.C is func)


@istest
def elem_iter():
    """
    Unit: Enum Util Iteration
    Tests that iteration over an enum produces the sequence of elements in that
    enum.
    """
    x = Enum(A=1, B=2, C=3)
    x_set = set(v for v in x)
    assert 'A' in x_set
    assert 'B' in x_set
    assert 'C' in x_set
