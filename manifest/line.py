#!/usr/bin/python

from __future__ import print_function
from os.path import join as pjoin

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

    def set_dir(self, dirname):
        """
        Set the directory name for a line object.
        This specifies the directory in which files with relative
        paths can be found.
        """
        self.dirname = dirname

class FileLine(Line):
    def __init__(self, rawline, permissions, owner, group, filename, destination):
        Line.__init__(self, rawline, filename)
        # dest is a path
        self.destination = destination
        # permissions are ugo style
        self.permissions = permissions
        self.owner = owner
        self.group = group
        # the directory for the source file is unknown from a raw parse
        self.dirname = None

    def set_dir(self, dirname):
        Line.set_dir(self, dirname)
        self.filename = pjoin(dirname, self.filename)

class CommandLine(Line):
    def __init__(self, rawline, cmd):
        Line.__init__(self, rawline)
        self.cmd = cmd

class ManifestLine(Line):
    def __init__(self, rawline, filename):
        Line.__init__(self, rawline, filename)

    def set_dir(self, dirname):
        Line.set_dir(self, dirname)
        self.filename = pjoin(dirname, self.filename)

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

def parse_line(s,dirname):
    import shlex
    ss = shlex.split(s, comments=True)
    if len(ss) is 0:
        return EmptyLine(s)
    try:
        # grab the constructor (line part 0), out of the typemap
        constr = LINE_TYPES[ss[0]]
        # feed in the rawline as the first argument to the constructor
        # followed by the rest of the line, as an expanded list
        args = ss[1:]
        line_obj = constr(s,*args)
        # set all filenames in the line object to absolute paths
        line_obj.set_dir(dirname)
        return line_obj
    except:
        raise ValueError('Invalid manifest line: %s' % s)

def manifest_expand(line_obj):
    ret = []
    with open(line_obj.filename) as manifest:
        for l in manifest:
            ret.append(parse_line(l,line_obj.dirname))
    return ret
