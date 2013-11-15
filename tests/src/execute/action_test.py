#!/usr/bin/python

from nose.tools import istest
from mock import patch

from tests.utils.exceptions import ensure_except

import src.execute.action as action

class MockProcess(object):
    def __init__(self):
        self.returncode = 0
    def wait(self):
        pass

@istest
def action_is_abstract():
    ensure_except(TypeError,action.Action)

@istest
def empty_action_list():
    done_actions = []
    def mock_execute(self):
        done_actions.append(self)

    # Just ensuring that an empty action list is valid
    with patch('src.execute.action.Action.execute',mock_execute):
        actions = action.ActionList([])
        actions.execute()

    assert len(done_actions) == 0

@istest
def empty_shell_action():
    # ensures that empty shell actions are valid (but silly)
    a = action.ShellAction([])

@istest
def shell_action_basic():
    # we patch Popen to prevent an attempt to actually invoke the
    # commands passed in
    # instead, commands are stored in the done_commands list
    done_commands = []
    def mock_Popen(commands, stdout=None, stderr=None, shell=None):
        done_commands.append(commands)
        return MockProcess()

    with patch('subprocess.Popen',mock_Popen):
        a = action.ShellAction(['mkdir /a/b'])
        a.execute()

    assert done_commands[0] == 'mkdir /a/b'

@istest
def action_list_inorder():
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
            a = action.ShellAction(['a b'])
            b = action.ShellAction(['p q r'])
            al = action.ActionList([a,b])
            al.execute()

    assert done_actions[0] == a
    assert done_actions[1] == b

    assert done_commands[0] == 'a b'
    assert done_commands[1] == 'p q r'

@istest
def failed_shell_action():
    def mock_Popen(commands, stdout=None, stderr=None, shell=None):
        """
        Produces a dummy failure process. We don't bother about the
        done_commands list here because it is not relevant.
        """
        p = MockProcess()
        p.returncode = 1
        return p

    with patch('subprocess.Popen',mock_Popen):
        a = action.ShellAction(['touch /a/b'])
        ensure_except(action.ActionException,a.execute)
