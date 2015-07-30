#!/usr/bin/python

from salve import paths


class FileContext(object):
    """
    Identifies a location in the manifest tree by filename and lineno.
    """
    def __init__(self, filename, lineno=None):
        """
        FileContext initializer.

        Args:
            @filename
            The file identified by the context.

        KWArgs:
            @lineno=None
            The line number identified by the context. When None, it means that
            there is no meaningful line number.
        """
        self.filename = paths.clean_path(filename)
        self.lineno = lineno

    def __str__(self):
        if self.lineno is None:
            return self.filename
        else:
            return self.filename + ', line ' + str(self.lineno)

    def __repr__(self):
        contents = 'filename=' + self.filename
        if self.lineno is not None:
            contents = contents + ',lineno=' + str(self.lineno)
        return 'FileContext(' + contents + ')'
