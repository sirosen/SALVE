#!/usr/bin/python

import src.util.locations as locations
import src.util.log as log

from src.settings.default_globals import apply_exec_context_defaults
from src.util.enum import Enum

context_types = Enum('STREAM', 'EXEC')


class StreamContext(object):
    """
    Identifies a location in the manifest tree by filename and lineno.
    """
    def __init__(self, filename, lineno):
        """
        StreamContext constructor.

        Args:
            @filename
            The file identified by the context.
            @lineno
            The line number identified by the context.
        """
        self.filename = locations.clean_path(filename)
        self.lineno = lineno

    def __str__(self):
        return self.filename + ', line ' + str(self.lineno)


class ExecutionContext(object):
    """
    Identifies the phase of execution, and carries any global or shared data
    from phase to phase.
    """
    phases = Enum('STARTUP', 'PARSING', 'ACTION_CONVERSION', 'VERIFICATION',
                  'EXECUTION')

    def __init__(self, startphase=phases.STARTUP):
        self.phase = startphase
        self.vars = {}
        apply_exec_context_defaults(self)

    def __str__(self):
        return self.phase

    def transition(self, newphase):
        assert newphase in self.phases
        self.phase = newphase

    def set(self, key, value):
        self.vars[key] = value

    def get(self, key):
        return self.vars[key]

    def has(self, key):
        return key in self.vars


class SALVEContext(object):
    """
    A wrapper that contains all available context types. This is used to pass
    contexts easily and uniformly from component to component, without the need
    for explicit passes of each context type.
    """
    def __init__(self, stream_context=None, exec_context=None):
        self.stream_context = stream_context
        self.exec_context = exec_context

    def has_context(self, ctx_type):
        if ctx_type == context_types.STREAM:
            return self.stream_context is not None
        elif ctx_type == context_types.EXEC:
            return self.exec_context is not None
        else:
            return False

    def shallow_copy(self):
        new = SALVEContext()
        if self.has_context(context_types.STREAM):
            new.stream_context = self.stream_context
        if self.has_context(context_types.EXEC):
            new.exec_context = self.exec_context
        return new

    def __str__(self):
        components = []
        if self.exec_context:
            components.append('[' + str(self.exec_context) + ']')
        if self.stream_context:
            components.append(str(self.stream_context))

        return ' '.join(components)

    def transition(self, newphase):
        assert self.exec_context is not None
        if newphase != self.exec_context.phase:
            transition_text = ('SALVE Execution Phase Transition ' +
                               '[%s] -> [%s]' %
                               (self.exec_context.phase, newphase))
            log.info(transition_text, self, print_context=False,
                 min_verbosity=3)
            self.exec_context.transition(newphase)
