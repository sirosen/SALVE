#!/usr/bin/python

from nose.tools import istest
import mock

from tests.util import ensure_except, scratch
from salve.context import FileContext

from salve.action import ShellAction
from salve.exceptions import ActionException
from salve.filesys import ConcreteFilesys


class MockProcess(object):
    def __init__(self):
        self.returncode = 0

    def wait(self):
        pass

    def communicate(self):
        return None, None


dummy_file_context = FileContext('no such file')


class TestWithScratchdir(scratch.ScratchContainer):
    @istest
    def shell_action_basic(self):
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
            a = ShellAction('mkdir /a/b', dummy_file_context)
            a.execute(ConcreteFilesys())

        assert len(done_commands) == 1
        assert done_commands[0] == 'mkdir /a/b'

    @istest
    def failed_shell_action(self):
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
            a = ShellAction(['touch /a/b'], dummy_file_context)
            ensure_except(ActionException, a.execute, ConcreteFilesys())
