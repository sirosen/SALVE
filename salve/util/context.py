#!/usr/bin/python

import salve

from salve.util import locations
from salve.util.enum import Enum


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
        self.filename = locations.clean_path(filename)
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


class ExecutionContext(object):
    """
    Identifies the phase of execution, and carries any global or shared data
    from phase to phase.
    """
    phases = Enum('STARTUP', 'PARSING', 'COMPILATION', 'VERIFICATION',
                  'EXECUTION')

    def __init__(self, startphase=phases.STARTUP):
        self.phase = startphase
        self.vars = {}

    def __str__(self):
        return self.phase

    def transition(self, newphase, quiet=False):
        assert newphase in self.phases

        if self.phase == newphase:
            return

        if not quiet:
            transition_text = ('SALVE Execution Phase Transition ' +
                               '[%s] -> [%s]' %
                               (self.phase, newphase))
            salve.logger.info(transition_text, hide_context=True,
                    min_verbosity=3)

        self.phase = newphase

    def set(self, key, value):
        self.vars[key] = value

    def get(self, key):
        return self.vars[key]

    def has(self, key):
        return key in self.vars
