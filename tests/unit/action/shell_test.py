#!/usr/bin/python

from nose.tools import istest
import mock

from tests.util import ensure_except
from salve.context import ExecutionContext, FileContext

from salve import action
from salve.action import shell
from salve.filesys import real_fs


class MockProcess(object):
    def __init__(self):
        self.returncode = 0

    def wait(self):
        pass

    def communicate(self):
        return None, None

dummy_file_context = FileContext('no such file')
dummy_exec_context = ExecutionContext()
dummy_exec_context.set('log_level', set())


@istest
def shell_action_basic():
    """
    Unit: Action Shell Singleton Command List
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

    with mock.patch('subprocess.Popen', mock_Popen):
        a = shell.ShellAction('mkdir /a/b', dummy_file_context)
        a.execute(real_fs)

    assert len(done_commands) == 1
    assert done_commands[0] == 'mkdir /a/b'


@istest
def failed_shell_action():
    """
    Unit: Action Shell Failure Raises Exception
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

    with mock.patch('subprocess.Popen', mock_Popen):
        a = shell.ShellAction(['touch /a/b'], dummy_file_context)
        ensure_except(action.ActionException, a.execute, real_fs)
