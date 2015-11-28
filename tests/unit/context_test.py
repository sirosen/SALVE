from nose.tools import istest, eq_

from tests.framework import ensure_except
from salve import context


basic_filectx1 = context.FileContext('/a/b/c', lineno=10)


@istest
def filectx_tostring():
    """
    Unit: FileContext to String
    Tests the conversion from a FileContext to a string.
    """
    eq_(str(basic_filectx1), '/a/b/c, line 10')


@istest
def filectx_repr():
    """
    Unit: FileContext Invoke repr()
    Tests the conversion from a FileContext to a string using __repr__
    """
    eq_(repr(basic_filectx1), 'FileContext(filename=/a/b/c,lineno=10)')


@istest
def execctx_tostring():
    """
    Unit: ExecutionContext to String
    Tests the conversion from an ExecutionContext to a string.
    """
    ctx = context.ExecutionContext(
        startphase=context.ExecutionContext.phases.STARTUP)
    eq_(str(ctx), 'STARTUP')


@istest
def execctx_transition():
    """
    Unit: ExecutionContext Phase Transition
    Tests that phase transitions have the expected result.
    """
    ctx = context.ExecutionContext(
        startphase=context.ExecutionContext.phases.STARTUP)
    ctx.transition(context.ExecutionContext.phases.EXECUTION, quiet=True)
    eq_(ctx.phase, 'EXECUTION')
    ctx.transition('STARTUP', quiet=True)
    eq_(ctx.phase, 'STARTUP')


@istest
def execctx_transition_failure_nonexistent():
    """
    Unit: ExecutionContext Phase Transition Failure (Non-Existent Phase)
    Tests that phase transitions fail if given a nonexistent phase.
    """
    ctx = context.ExecutionContext(
        startphase=context.ExecutionContext.phases.STARTUP)
    ensure_except(AssertionError, ctx.transition, 'STARTUP2')


@istest
def execctx_contains():
    """
    Unit: ExecutionContext Contains Value
    Tests the __contains__ method on an execution context to make sure that it
    works.
    """
    ctx = context.ExecutionContext(
        startphase=context.ExecutionContext.phases.STARTUP)
    ctx['x'] = 1
    assert 'x' in ctx
