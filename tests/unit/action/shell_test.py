from nose.tools import istest
import mock

from tests.framework import ensure_except, scratch
from salve.context import FileContext

from salve.action import ShellAction
from salve.exceptions import ActionException
from salve.filesys import ConcreteFilesys


dummy_file_context = FileContext('no such file')


class TestWithScratchdir(scratch.ScratchContainer):
    @istest
    @mock.patch('subprocess.Popen')
    def shell_action_basic(self, mock_popen):
        """
        Unit: Action Shell Singleton Command List
        Verifies that executing a ShellAction with one command runs that
        command.
        """
        mock_popen.return_value.returncode = 0

        ShellAction('mkdir /a/b', dummy_file_context)(ConcreteFilesys())

        assert mock_popen.called_once_with(['mkdir', '/a/b'])

    @istest
    @mock.patch('subprocess.Popen')
    def failed_shell_action(self, mock_popen):
        """
        Unit: Action Shell Failure Raises Exception
        Verifies that executing a ShellAction raises an exception if one of
        the commands in it returns a nonzero status.
        """
        mock_popen.return_value.returncode = 1

        a = ShellAction(['touch /a/b'], dummy_file_context)
        ensure_except(ActionException, a.execute, ConcreteFilesys())
