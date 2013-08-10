#!/usr/bin/python

class Line(object):
    def __init__(self, filename=None):
        from os.path import exists
        # Most lines are associated with files, but
        # some, like execute lines, are not necessarily
        if filename is not None:
            if not exists(filename):
                raise IOError('Nonexistent file in manifest: %s' % filename)
            self.filename = filename

class FileLine(Line):
    def __init__(self, permissions, owner, group, filename, destination):
        Line.__init__(self, filename)
        self.destination = destination
        self.permissions = permissions
        self.owner = owner
        self.group = group

class CommandLine(Line):
    def __init__(self, cmd):
        Line.__init__(self)
        self.cmd = cmd

class ManifestLine(Line):
    def __init__(self, filename):
        Line.__init__(self, filename)

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
    ss = shlex.split(s)
    try:
        # grab the type (line part 0)
        ty = ss[0]
        # feed the rest of the line, as an expanded list,
        # into the constructor that the line type maps to
        args = ss[1:]
        return LINE_TYPES[ty](*args)
    except:
        raise
