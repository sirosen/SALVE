#!/usr/bin/python

from nose.tools import istest
from mock import patch

from tests.utils.exceptions import ensure_except
from src.util.error import StreamContext

import src.execute.action as action

class MockProcess(object):
    def __init__(self):
        self.returncode = 0
    def wait(self):
        pass
    def communicate(self):
        return None,None

dummy_context = StreamContext('no such file',-1)

@istest
def action_is_abstract():
    """
    Action Base Class Is Abstract
    Verifies that instantiating an Action raises an error.
    """
    ensure_except(TypeError,action.Action)

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
    with patch('src.execute.action.Action.execute',mock_execute):
        actions = action.ActionList([],dummy_context)
        actions.execute()

    assert len(done_actions) == 0

@istest
def empty_shell_action():
    """
    Action Shell Empty Command List Is No-Op
    Verifies that executing an empty ShellAction does nothing.
    """
    # ensures that empty shell actions are valid (but silly)
    a = action.ShellAction([],dummy_context)

@istest
def shell_action_basic():
    """
    Action Shell Singleton Command List
    Verifies that executing a ShellAction with one command runs that
    command.
    """
    # we patch Popen to prevent an attempt to actually invoke the
    # commands passed in
    # instead, commands are stored in the done_commands list
    done_commands = []
    def mock_Popen(commands, stdout=None, stderr=None, shell=None):
        done_commands.append(commands)
        return MockProcess()

    with patch('subprocess.Popen',mock_Popen):
        a = action.ShellAction('mkdir /a/b',dummy_context)
        a.execute()

    assert done_commands[0] == 'mkdir /a/b'

@istest
def action_list_inorder():
    """
    Action List Execute In Order
    Verifies that executing an ActionList runs the actions in it in the
    specified order.
    """
    done_actions = []
    # this ref is used to avoid a recursive loop, since we patch
    # execute with mock_execute
    real_execute = action.ShellAction.execute
    def mock_execute(self):
        real_execute(self)
        done_actions.append(self)

    # we patch Popen to prevent an attempt to actually invoke the
    # commands passed in
    # instead, commands are stored in the done_commands list
    done_commands = []
    def mock_Popen(commands, stdout=None, stderr=None, shell=None):
        done_commands.append(commands)
        return MockProcess()

    with patch('src.execute.action.ShellAction.execute',mock_execute):
        with patch('subprocess.Popen',mock_Popen):
            a = action.ShellAction('a b',dummy_context)
            b = action.ShellAction('p q r',dummy_context)
            al = action.ActionList([a,b],dummy_context)
            al.execute()

    assert done_actions[0] == a
    assert done_actions[1] == b
    assert done_commands[0] == 'a b'
    assert done_commands[1] == 'p q r'

@istest
def failed_shell_action():
    """
    Action Shell Failure Raises Exception
    Verifies that executing a ShellAction raises an exception if one of
    the commands in it returns a nonzero status.
    """
    def mock_Popen(commands, stdout=None, stderr=None, shell=None):
        """
        Produces a dummy failure process. We don't bother about the
        done_commands list here because it is not relevant.
        """
        p = MockProcess()
        p.returncode = 1
        return p

    with patch('subprocess.Popen',mock_Popen):
        a = action.ShellAction(['touch /a/b'],dummy_context)
        ensure_except(action.ActionException,a.execute)
