#!/usr/bin/python

import abc, subprocess

from src.util.error import SALVEException

class ActionException(SALVEException):
    """
    A SALVE exception specialized for Actions.
    """
    def __init__(self,msg,ctx):
        """
        ActionException constructor

        Args:
            @msg
            A string message that describes the error.
            @ctx
            A StreamContext that identifies the origin of this
            exception.
        """
        SALVEException.__init__(self,msg,ctx)

class Action(object):
    """
    An Action is the basis of execution.
    Actions can perform arbitrary modifications to the OS or filesystem,
    but typically are limited to moving and creating files and
    directories explicitly.
    There is no meaningful generic Action, so this is an ABC.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self,context):
        """
        Base Action constructor.

        Args:
            @context
            The StreamContext from which this Action originates. Usually
            this can be traced directly to a Block that generated the
            Action. Used to identify the origin of any errors that are
            tripped during the Action's creation or execution.
        """
        self.context = context

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

class ShellAction(Action):
    """
    A ShellAction is one of the basic Action types, used to invoke
    shell subprocesses.
    """
    def __init__(self, command, context):
        """
        ShellAction constructor.

        Args:
            @command
            A string that defines the shell command to execute when the
            ShellAction is invoked.
            @context
            The ShellAction's StreamContext.
        """
        Action.__init__(self,context)
        self.cmd = command

    def __str__(self):
        return 'ShellAction('+str(self.cmd)+')'

    def execute(self):
        """
        ShellAction execution.

        Invokes the ShellAction's command, and fails if it returns a
        nonzero exit code, and returns its stdout and stderr.
        """
        # run the command, passing output to PIPE
        process = subprocess.Popen(self.cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True)
        # Popen is asynchronous without an invocation of wait()
        process.wait()
        # check if returncode became nonzero, and fail if it did
        if process.returncode != 0:
            raise ActionException(str(self)+\
                ' failed with exit code '+str(process.returncode),
                self.context)

        return process.communicate()

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
            The StreamContext for the AL.
        """
        Action.__init__(self,context)
        self.actions = act_lst

    def __iter__(self):
        """
        Iterating over an AL iterates over its sub-actions.
        """
        for act in self.actions: yield act

    def __str__(self):
        return "ActionList("+";".join(str(a) for a in self.actions)+\
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
