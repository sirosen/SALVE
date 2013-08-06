#!/usr/bin/python

class Line(object):
    def __init__(self,filename):
        self.filename = filename

class FileLine(Line):
    def __init__(self, permissions, owner, group, filename, destination):
        Line.__init__(self,filename)
        self.destination = destination
        self.permissions = permissions
        self.owner = owner
        self.group = group

class CommandLine(Line):
    def __init__(self, filename, *args):
        Line.__init__(self, filename)
        self.args = args

LINE_TYPES = {
        'x':CommandLine,
        'execute':CommandLine,
        'f':FileLine,
        'file':FileLine
        }

def parse_line(s):
    import shlex
    ss = shlex.split(s)
    try:
        ty = ss[0]
        return LINE_TYPES[ty](*ss[1:])
    except:
        raise
