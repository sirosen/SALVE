#!/usr/bin/python

from __future__ import print_function
import abc, subprocess

class ActionException(StandardError):
    """
    A barebones specialized exception for Action creation and execution
    errors.
    """
    def __init__(self,msg):
        StandardError.__init__(self,msg)
        self.message = msg 

class Action(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def execute(self): pass #pragma: no cover

class ShellAction(Action):
    def __init__(self, command_list):
        self.cmds = command_list

    def __str__(self):
        return 'ShellAction(['+str(self.cmds)+'])'
     
    def execute(self):
        for cmd in self.cmds:
            process = subprocess.Popen(cmd,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       shell=True)
            process.wait()
            if process.returncode != 0:
                raise ActionException(str(self)+\
                    ' failed with exit code '+str(process.returncode)+\
                    ' on command "' + cmd + '"')

class ActionList(Action):
    def __init__(self, act_lst):
        self.actions = act_lst

    def execute(self):
        for a in self.actions:
            a.execute()

class ParallelActionBag(Action):
    def __init__(self, act_lst):
        self.actions = set(act_lst) #pragma: no cover

    def execute(self):
        # stub, not implemented
        # idea: create a thread pool, spin off a management
        # thread for the thread pool which feeds it tasks
        # from the bag
        # meanwhile, the main thread of execution tries
        # to down a binary semaphore
        # when there are no more tasks and all threads in
        # the pool are idling, the management thread
        # ups the semaphore and does cleanup
        pass #pragma: no cover
