#!/usr/bin/python

import mock
from nose.tools import istest
from tests.utils.exceptions import ensure_except

import src.util.context as context

@istest
def streamctx_tostring():
    """
    StreamContext to String
    Tests the conversion from a StreamContext to a string.
    """
    ctx = context.StreamContext('/a/b/c',10)
    assert str(ctx) == '/a/b/c, line 10', str(ctx)

@istest
def execctx_tostring():
    """
    ExecutionContext to String
    Tests the conversion from an ExecutionContext to a string.
    """
    ctx = context.ExecutionContext(
        startphase=context.ExecutionContext.phases.STARTUP)
    assert str(ctx) == 'STARTUP'

@istest
def salvectx_tostring():
    """
    SALVEContext to String
    Tests the conversion from an SALVEContext to a string.
    """
    stream_ctx = context.StreamContext('p/q',2)
    exec_ctx = context.ExecutionContext(
        startphase=context.ExecutionContext.phases.STARTUP)
    ctx = context.SALVEContext(stream_context=stream_ctx,
                               exec_context=exec_ctx)
    assert str(ctx) == '[STARTUP] p/q, line 2'

@istest
def salvectx_tostring_noexec():
    """
    SALVEContext to String (no exec)
    Tests the conversion from an SALVEContext to a string without an
    ExecutionContext.
    """
    stream_ctx = context.StreamContext('p/q',2)
    ctx = context.SALVEContext(stream_context=stream_ctx)
    assert str(ctx) == 'p/q, line 2'

@istest
def salvectx_tostring_nostream():
    """
    SALVEContext to String (no stream)
    Tests the conversion from an SALVEContext to a string without a
    StreamContext.
    """
    exec_ctx = context.ExecutionContext(
        startphase=context.ExecutionContext.phases.STARTUP)
    ctx = context.SALVEContext(exec_context=exec_ctx)
    assert str(ctx) == '[STARTUP]'

@istest
def execctx_transition():
    """
    ExecutionContext Phase Transition
    Tests that phase transitions have the expected result.
    """
    ctx = context.ExecutionContext(
        startphase=context.ExecutionContext.phases.STARTUP)
    ctx.transition(context.ExecutionContext.phases.EXECUTION)
    assert ctx.phase == 'EXECUTION'
    ctx.transition('STARTUP')
    assert ctx.phase == 'STARTUP'

@istest
def execctx_transition_failure_nonexistent():
    """
    ExecutionContext Phase Transition Failure (Non-Existent Phase)
    Tests that phase transitions fail if given a nonexistent phase.
    """
    ctx = context.ExecutionContext(
        startphase=context.ExecutionContext.phases.STARTUP)
    ensure_except(AssertionError,ctx.transition,'STARTUP2')

@istest
def salvectx_has_streamctx():
    """
    SALVEContext Has StreamContext (positive)
    Tests the has_context() check for a SALVEContext with a StreamContext.
    """
    stream_ctx = context.StreamContext('p/q',2)
    ctx = context.SALVEContext(stream_context=stream_ctx)
    assert ctx.has_context(context.SALVEContext.ctx_types.STREAM)

@istest
def salvectx_not_has_streamctx():
    """
    SALVEContext Has StreamContext (negative)
    Tests the has_context() check for a SALVEContext without a StreamContext.
    """
    ctx = context.SALVEContext()
    assert not ctx.has_context(context.SALVEContext.ctx_types.STREAM)

@istest
def salvectx_has_execctx():
    """
    SALVEContext Has ExecutionContext (positive)
    Tests the has_context() check for a SALVEContext with an ExecutionContext.
    """
    exec_ctx = context.ExecutionContext(
        startphase=context.ExecutionContext.phases.STARTUP)
    ctx = context.SALVEContext(exec_context=exec_ctx)
    assert ctx.has_context(context.SALVEContext.ctx_types.EXEC)

@istest
def salvectx_not_has_execctx():
    """
    SALVEContext Has ExecutionContext (negative)
    Tests the has_context() check for a SALVEContext without an ExecutionContext.
    """
    ctx = context.SALVEContext()
    assert not ctx.has_context(context.SALVEContext.ctx_types.EXEC)

@istest
def salvectx_not_has_invalidctx():
    """
    SALVEContext Does Not Have Invalid Context Type
    Tests the has_context() check for a SALVEContext with an invalid context type.
    """
    ctx = context.SALVEContext()
    assert not ctx.has_context('INVALID CTX TYPE')

@istest
def salvectx_shallow_copy():
    """
    SALVEContext Shallow Copy
    Tests that a shallow copy of a SALVEContext contains the same contexts, but
    is not a ref to the same object.
    """
    stream_ctx = context.StreamContext('p/q',2)
    exec_ctx = context.ExecutionContext(
        startphase=context.ExecutionContext.phases.STARTUP)
    ctx = context.SALVEContext(stream_context=stream_ctx,
                               exec_context=exec_ctx)
    ctx2 = ctx.shallow_copy()

    assert ctx is not ctx2
    assert ctx.stream_context is ctx2.stream_context
    assert ctx.exec_context is ctx2.exec_context
