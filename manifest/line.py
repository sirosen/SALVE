#!/usr/bin/python

from __future__ import print_function
from collections import namedtuple

class Line(object):
    def __init__(self, rawline, filename=None):
        # All lines contain their original string
        self.rawline = rawline

        # Most lines are associated with files, but
        # some, like execute lines, are not necessarily
        if filename is not None:
            self.filename = filename
            # import here could keep the os.path module out of
            # runs that use SALVE just to run batches of commands
            # Not expected, but valid and supported
            from os.path import exists
            if not exists(filename):
                from sys import stderr
                print('Nonexistent file in manifest (we hope that you generate it before use): %s' % filename,file=stderr)

class FileLine(Line):
    def __init__(self, rawline, permissions, owner, group, filename, destination):
        Line.__init__(self, rawline, filename)
        # dest is a path
        self.destination = destination
        # permissions are ugo style
        self.permissions = permissions
        self.owner = owner
        self.group = group

class CommandLine(Line):
    def __init__(self, rawline, cmd):
        Line.__init__(self, rawline)
        self.cmd = cmd

class ManifestLine(Line):
    def __init__(self, rawline, filename):
        Line.__init__(self, rawline, filename)

class EmptyLine(Line):
    def __init__(self, rawline):
        Line.__init__(self, rawline)

LINE_TYPES = {
        'x':CommandLine,
        'execute':CommandLine,
        'f':FileLine,
        'file':FileLine,
        'm':ManifestLine,
        'manifest':ManifestLine
        }

def parse_line(s):
    import shlex
    ss = shlex.split(s, comments=True)
    if len(ss) is 0:
        return EmptyLine(s)
    try:
        # grab the type (line part 0), out of the typemap
        ty = LINE_TYPES[ss[0]]
        # feed in the rawline as the first argument to the constructor
        # that the type maps to
        args = ss[1:]
        # feed in the rest of the line, as an expanded list
        return ty(s,*args)
    except SyntaxWarning:
        pass
    except:
        raise ValueError('Invalid manifest line: %s' % s)
