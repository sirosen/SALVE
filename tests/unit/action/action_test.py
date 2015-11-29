import mock
from nose.tools import istest, eq_, ok_
from nose_parameterized import parameterized

from tests.framework import ensure_except, scratch, first_param_docfunc
from tests.unit.action import dummy_file_context

from salve.exceptions import ActionException
from salve.action import Action, DynamicAction, ActionList
from salve.filesys import ConcreteFilesys


class TestWithScratchdir(scratch.ScratchContainer):
    @parameterized.expand(
        [('Unit: Action Base Class Is Abstract', Action),
         ('Unit: Dynamic Action Base Class Is Abstract', DynamicAction)],
        testcase_func_doc=first_param_docfunc)
    @istest
    def base_action_classes_abc(self, description, klass):
        ensure_except(TypeError, klass, dummy_file_context)

    @istest
    def dynamic_action_execute_fails(self):
        """
        Unit: Dynamic Action No Execute Fails
        Checks that a DynamicAction which doesn't create an execute method when
        it generates will trigger an ActionException
        """
        class DummyAction(DynamicAction):
            def generate(self):
                pass

        act = DummyAction(dummy_file_context)
        ensure_except(ActionException, act.execute, ConcreteFilesys())

    @istest
    def dynamic_action_call_generates_and_executes(self):
        """
        Unit: Dynamic Action Invocation Generates & Executes
        Verifies that calling a DynamicAction invokes its generation
        function and then its execution function, even when generation
        rewrites execution.
        """
        mock_exec = mock.Mock()
        mock_fs = mock.Mock()

        class DummyAction(DynamicAction):
            def generate(self):
                self.execute = mock_exec
        DummyAction(dummy_file_context)(mock_fs)

        mock_exec.assert_called_once_with(mock_fs)

    @istest
    def empty_action_list(self):
        """
        Unit: Action List Empty List Is No-Op
        Verifies that executing an empty ActionList does nothing.
        """
        # Just ensuring that an empty action list is valid
        with mock.patch('salve.action.Action.execute',
                        autospec=True) as mock_exec:
            actions = ActionList([], dummy_file_context)
            actions(ConcreteFilesys())

            assert not mock_exec.called

    @istest
    def empty_action_list_to_string(self):
        """
        Unit: Action List Empty List String Representation

        Checks the string repr of an empty AL.
        """
        eq_(str(ActionList([], dummy_file_context)),
            'ActionList([],context={0!r})'.format(dummy_file_context))

    @istest
    def action_list_inorder(self):
        """
        Unit: Action List Execute In Order
        Verifies that executing an ActionList runs the actions in it in the
        specified order.
        """
        class DummyAction(Action):
            def execute(self, filesys):
                raise NotImplementedError()
        mock_exec = mock.create_autospec(DummyAction.execute)
        DummyAction.execute = mock_exec

        a = DummyAction(dummy_file_context)
        b = DummyAction(dummy_file_context)
        fs = ConcreteFilesys()
        ActionList([a, b], dummy_file_context)(fs)

        mock_exec.assert_has_calls([mock.call(a, fs), mock.call(b, fs)])

    @istest
    def action_verifies_OK(self):
        """
        Unit: Action Verification Defaults To OK
        Verifies that an action verification on an action which does not
        override verification will produce an OK status.
        """
        class DummyAction(Action):
            def execute(self):
                raise NotImplementedError()

        ok_(DummyAction(dummy_file_context).verify_can_exec(ConcreteFilesys()))
