#!/usr/bin/python

import abc, subprocess

from src.util.error import SALVEException

class ActionException(SALVEException):
    """
    A barebones specialized exception for Action creation and execution
    errors.
    """
    def __init__(self,msg,ctx):
        SALVEException.__init__(self,msg,ctx)

class Action(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self,context):
        self.context = context

    @abc.abstractmethod
    def execute(self): pass #pragma: no cover

class ShellAction(Action):
    def __init__(self, command, context):
        Action.__init__(self,context)
        self.cmd = command

    def __str__(self):
        return 'ShellAction('+str(self.cmd)+')'

    def execute(self):
        process = subprocess.Popen(self.cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True)
        process.wait()
        if process.returncode != 0:
            raise ActionException(str(self)+\
                ' failed with exit code '+str(process.returncode),
                self.context)
        return process.communicate()

class ActionList(Action):
    def __init__(self, act_lst, context):
        Action.__init__(self,context)
        self.actions = act_lst

    def __str__(self):
        return "ActionList("+";".join(str(a) for a in self.actions)+\
               "context="+str(self.context)+")"

    def append(self,act):
        assert isinstance(act, Action)
        self.actions.append(act)

    def prepend(self,act):
        assert isinstance(act, Action)
        self.actions.insert(0,act)

    def execute(self):
        for a in self.actions:
            a.execute()
