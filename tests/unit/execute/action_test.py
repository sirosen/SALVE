#!/usr/bin/python

import mock
from nose.tools import istest

from tests.utils.exceptions import ensure_except
from salve.util.context import SALVEContext, ExecutionContext, StreamContext

import salve.execute.action as action

dummy_stream_context = StreamContext('no such file', -1)
dummy_exec_context = ExecutionContext()
dummy_context = SALVEContext(stream_context=dummy_stream_context,
                             exec_context=dummy_exec_context)


@istest
def action_is_abstract():
    """
    Action Base Class Is Abstract
    Verifies that instantiating an Action raises an error.
    """
    ensure_except(TypeError, action.Action)


@istest
def dynamic_action_is_abstract():
    """
    Dynamic Action Base Class Is Abstract
    Verifies that instantiating a DynamicAction raises an error.
    """
    ensure_except(TypeError, action.DynamicAction)


@istest
def dynamic_action_execute_fails():
    """
    Dynamic Action Invocation Generates & Executes
    Verifies that calling a DynamicAction invokes its generation
    function and then its execution function, even when generation
    rewrites execution.
    """
    logged_funcs = []

    class DummyAction(action.DynamicAction):
        def generate(self):
            pass

    act = DummyAction(dummy_context)
    ensure_except(action.ActionException, act.execute)


@istest
def dynamic_action_call_generates_and_executes():
    """
    Dynamic Action Invocation Generates & Executes
    Verifies that calling a DynamicAction invokes its generation
    function and then its execution function, even when generation
    rewrites execution.
    """
    logged_funcs = []

    class DummyAction(action.DynamicAction):
        def generate(self):
            logged_funcs.append('generate')

            def execute_replacement():
                logged_funcs.append('execute_replacement')
            self.execute = execute_replacement

    act = DummyAction(dummy_context)
    act()

    assert len(logged_funcs) == 2
    assert logged_funcs[0] == 'generate'
    assert logged_funcs[1] == 'execute_replacement'


@istest
def empty_action_list():
    """
    Action List Empty List Is No-Op
    Verifies that executing an empty ActionList does nothing.
    """
    done_actions = []

    def mock_execute(self):
        done_actions.append(self)

    # Just ensuring that an empty action list is valid
    with mock.patch('salve.execute.action.Action.execute', mock_execute):
        actions = action.ActionList([], dummy_context)
        actions.execute()

    assert len(done_actions) == 0


@istest
def empty_action_list_to_string():
    """
    Action List Empty List String Representation

    Checks the string repr of an empty AL.
    """
    act = action.ActionList([], dummy_context)

    assert str(act) == 'ActionList([],context=' + str(dummy_context) + ')'


@istest
def action_list_inorder():
    """
    Action List Execute In Order
    Verifies that executing an ActionList runs the actions in it in the
    specified order.
    """
    done_actions = []

    class DummyAction(action.Action):
        def __init__(self, ctx):
            action.Action.__init__(self, ctx)

        def execute(self):
            done_actions.append(self)

    a = DummyAction(dummy_context)
    b = DummyAction(dummy_context)
    al = action.ActionList([a, b], dummy_context)
    al.execute()

    assert done_actions[0] == a
    assert done_actions[1] == b


@istest
def action_verifies_OK():
    """
    Action Verification Defaults To OK
    Verifies that an action verification on an action which does not override
    verification will produce an OK status.
    """
    class DummyAction(action.Action):
        def __init__(self, ctx):
            action.Action.__init__(self, ctx)

        def execute(self):
            pass

    a = DummyAction(dummy_context)

    verify_code = a.verify_can_exec()

    assert verify_code == a.verification_codes.OK
