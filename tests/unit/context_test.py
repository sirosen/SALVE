#!/usr/bin/python

import mock
from nose.tools import istest

from tests.util import ensure_except
from salve import context


@istest
def filectx_tostring():
    """
    Unit: FileContext to String
    Tests the conversion from a FileContext to a string.
    """
    ctx = context.FileContext('/a/b/c', lineno=10)
    assert str(ctx) == '/a/b/c, line 10', str(ctx)


@istest
def filectx_repr():
    """
    Unit: FileContext Invoke repr()
    Tests the conversion from a FileContext to a string using __repr__
    """
    ctx = context.FileContext('/a/b/c', lineno=10)
    assert repr(ctx) == 'FileContext(filename=/a/b/c,lineno=10)', repr(ctx)


@istest
def execctx_tostring():
    """
    Unit: ExecutionContext to String
    Tests the conversion from an ExecutionContext to a string.
    """
    ctx = context.ExecutionContext(
        startphase=context.ExecutionContext.phases.STARTUP)
    assert str(ctx) == 'STARTUP'


@istest
def execctx_transition():
    """
    Unit: ExecutionContext Phase Transition
    Tests that phase transitions have the expected result.
    """
    ctx = context.ExecutionContext(
        startphase=context.ExecutionContext.phases.STARTUP)
    ctx.transition(context.ExecutionContext.phases.EXECUTION, quiet=True)
    assert ctx.phase == 'EXECUTION'
    ctx.transition('STARTUP', quiet=True)
    assert ctx.phase == 'STARTUP'


@istest
def execctx_transition_failure_nonexistent():
    """
    Unit: ExecutionContext Phase Transition Failure (Non-Existent Phase)
    Tests that phase transitions fail if given a nonexistent phase.
    """
    ctx = context.ExecutionContext(
        startphase=context.ExecutionContext.phases.STARTUP)
    ensure_except(AssertionError, ctx.transition, 'STARTUP2')
