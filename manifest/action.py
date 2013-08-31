#!/usr/bin/python

from __future__ import print_function
import line

def Action(object):
    def __init__(self, line_obj):
        self.line = line_obj
        self.cmds = []
        if isinstance(line_obj, line.EmptyLine):
            pass
        elif isinstance(line_obj, line.ManifestLine):
            raise ValueError('Cannot create an Action from a ManifestLine' +\
                             '-- manifests must be expanded before conversion.')
        elif isinstance(line_obj, line.CommandLine):
            self.cmds = [line_obj.cmd]
        elif isinstance(line_obj, line.FileLine):
            self.cmds = ['cp "%s" "%s"' % (line_obj.filename, line_obj.destination),
                         'chown %s:%s "%s"' % (line_obj.owner, line_obj.group, line_obj.destination),
                         'chmod %s "%s"' % (line_obj.permissions, line_obj.destination)
                        ]
     
    def execute(self):
        import subprocess, shlex
        for cmd in self.cmds:
            process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def ActionList(Action):
    def __init__(self, act_lst):
        self.actions = act_lst

    def execute(self):
        for a in self.actions:
            a.execute()

    def append(self, act):
        self.actions.append(act)

def ParallelActionBag(Action):
    def __init__(self, act_lst):
        self.actions = set(act_lst)

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
        pass
