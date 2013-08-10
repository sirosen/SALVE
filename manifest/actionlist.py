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
     
    def do(self):
        import subprocess, shlex
        for cmd in self.cmds:
            process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def ActionList(object):
    def __init__(self, line_objs):
        self.actions = []
        for l in line_objs:
            if isinstance(l, line.ManifestLine):
                self.concat(ActionList(manifest_expand(l)))
            elif isinstance(l, line.EmptyLine):
                pass
            else:
                self.actions.append(Action(l))

    def concat(self, other):
        self.actions = self.actions + other.actions
