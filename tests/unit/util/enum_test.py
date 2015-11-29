from nose.tools import istest, eq_, ok_

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
    eq_(x.A, 'A')
    ok_(x.B is y)


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
    eq_(x.A, 1)
    eq_(x.B, 'x.B')
    ok_(x.C is func)


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
    eq_(x.A, 'A')
    eq_(x.B, 'x.B')
    ok_(x.C is func)


@istest
def elem_iter():
    """
    Unit: Enum Util Iteration
    Tests that iteration over an enum produces the sequence of elements in that
    enum.
    """
    x = Enum(A=1, B=2, C=3)
    x_set = set(v for v in x)
    ok_('A' in x_set)
    ok_('B' in x_set)
    ok_('C' in x_set)
