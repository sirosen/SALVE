import mock
from nose.tools import istest

from salve.context import ExecutionContext, FileContext

from salve.action import create
from salve.filesys import ConcreteFilesys
from tests.util import scratch

dummy_file_context = FileContext('no such file')
dummy_exec_context = ExecutionContext()


class TestWithScratchdir(scratch.ScratchContainer):
    @istest
    @mock.patch('os.access', lambda x, y: True)
    @mock.patch('salve.filesys.concrete.open', create=True)
    def filecreate_execute(self, mock_open):
        """
        Unit: File Create Action Execution
        Needs to be in a scratchdir to ensure that there is no file
        named 'a' in the target dir.
        """
        a_name = self.get_fullname('a')

        fc = create.FileCreateAction(a_name, dummy_file_context)
        fc(ConcreteFilesys())

        mock_open.assert_called_once_with(a_name, 'a')
        handle = mock_open()
        assert len(handle.write.mock_calls) == 0

    @istest
    @mock.patch('os.access', lambda x, y: True)
    @mock.patch('os.makedirs')
    def dircreate_execute(self, mock_mkdirs):
        """
        Unit: Directory Create Action Execution
        Needs to be in a scratchdir to ensure that there is no directory
        named 'a' in the target dir.
        """
        a_name = self.get_fullname('a')

        dc = create.DirCreateAction(a_name, dummy_file_context)
        dc(ConcreteFilesys())

        mock_mkdirs.assert_called_once_with(a_name)


@istest
def filecreate_to_str():
    """
    Unit: File Create Action String Conversion
    """
    fc = create.FileCreateAction('a', dummy_file_context)

    assert str(fc) == ('FileCreateAction(dst=a,context=' +
                       repr(dummy_file_context) + ')')


@istest
def dircreate_to_str():
    """
    Unit: Directory Create Action String Conversion
    """
    dc = create.DirCreateAction('a', dummy_file_context)

    assert str(dc) == ('DirCreateAction(dst=a,context=' +
                       repr(dummy_file_context) + ')')
