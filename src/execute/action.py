#!/usr/bin/python

import abc

from src.util.error import SALVEException
from src.util.context import ExecutionContext
import src.util.enum as enum

class ActionException(SALVEException):
    """
    A SALVE exception specialized for Actions.
    """
    def __init__(self,msg,context):
        """
        ActionException constructor

        Args:
            @msg
            A string message that describes the error.
            @context
            A SALVEContext.
        """
        SALVEException.__init__(self,msg,context)

class Action(object):
    """
    An Action is the basis of execution.
    Actions can perform arbitrary modifications to the OS or filesystem,
    but typically are limited to moving and creating files and
    directories explicitly.
    There is no meaningful generic Action, so this is an ABC.
    """
    __metaclass__ = abc.ABCMeta

    # by default, the only verification code is OK
    verification_codes = enum.Enum('OK')

    def __init__(self,context):
        """
        Base Action constructor.

        Args:
            @context
            The SALVEContext.
        """
        self.context = context

    def verify_can_exec(self):
        """
        Verifies that the action can be executed. Returns a verification code
        from self.verification_codes.
        'OK' indicates that execution can proceed. Anything else is an error
        or warning code specific to the action type.
        """
        # transition to the action verification phase,
        # confirming execution will work
        self.context.transition(ExecutionContext.phases.VERIFICATION)
        return self.verification_codes.OK

    @abc.abstractmethod
    def execute(self):
        """
        Executes the Action.

        This is the only essential characteristic of an Action: that
        it can be executed to produce some effect.
        """
        pass #pragma: no cover

    def __call__(self, *args, **kwargs):
        """
        Executes the Action.

        In a sense, this is a better description of what the "execute"
        attribute is. Calling an Action and executing it are identical.
        """
        return self.execute(*args,**kwargs)

class DynamicAction(Action):
    """
    DynamicActions are actions that may not be executable at the time
    that they are instantiated. Is an ABC.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def generate(self):
        """
        Generates the action body -- can consist of a rewrite of
        self.execute(), for example -- so that when execution takes
        place, it will be valid / possible.
        """
        pass #pragma: no cover

    def execute(self):
        """
        DynamicAction.execute is not abstract because by default, the
        notion of execute on an ungenerated action is well defined.
        This needs to be overwritten during generation in most cases.
        """
        raise ActionException('Uninstantiated DynamicAction',
                              self.context)

    def __call__(self, *args, **kwargs):
        """
        Calling a DynamicAction invokes self-generation immediately
        followed by execution. This ensures that execution takes
        place with the most up-to-date information available.
        """
        self.generate()
        Action.__call__(self, *args, **kwargs)

class ActionList(Action):
    """
    An ActionList, often referred to internally as an "AL", is one of
    the basic Action types.

    It is used to provide a sequential list of other actions to execute.
    """
    def __init__(self, act_lst, context):
        """
        ActionList constructor.

        Args:
            @act_list
            A list of Action objects. No checking is performed, the
            class assumes that what it is handed is in fact a list of
            Action objects.

            @context
            The SALVEContext.
        """
        Action.__init__(self,context)
        self.actions = act_lst

    def __iter__(self):
        """
        Iterating over an AL iterates over its sub-actions.
        """
        for act in self.actions: yield act

    def __str__(self):
        return "ActionList(["+",".join(str(a) for a in self.actions)+'],'\
               "context="+str(self.context)+")"

    def append(self,act):
        """
        Append a new Action to the AL.

        Args:
            @act
            The action to append.
        """
        assert isinstance(act, Action)
        self.actions.append(act)

    def prepend(self,act):
        """
        Prepend a new Action to the AL.

        Args:
            @act
            The action to prepend.
        """
        assert isinstance(act, Action)
        self.actions.insert(0,act)

    def execute(self):
        """
        Execute the AL. Consists of a walk over the AL executing each
        of its sub-actions.
        """
        for act in self: act()
