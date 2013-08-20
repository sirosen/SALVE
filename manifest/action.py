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
    def __init__(self, line_objs):
        self.actions = []
        for l in line_objs:
            if isinstance(l, line.EmptyLine):
                pass
            else:
                self.actions.append(line_to_action(l))

    def execute(self):
        for a in self.actions:
            a.execute()

def ParallelActionBag(Action):
    def __init__(self, line_objs):
        self.actions = set()
        for l in line_objs:
            if isinstance(l, line.ManifestLine):
                self.actions.add(line_to_action(l))

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

def line_to_action(line_obj):
    if isinstance(line_obj, line.ManifestLine):
        return ActionList(line.manifest_expand(l))
    else:
        return Action(l)
