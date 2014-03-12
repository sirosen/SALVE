#!/usr/bin/python

import sys
import src.util.log as log

defaults = {
    'verbosity': 0,
    'run_log': sys.stderr,
    'log_level': set(log.log_types)
}

def apply_exec_context_defaults(exec_context,overwrite=False):
    """
    Apply the default globals to an ExecutionContext.

    Args:
        @exec_context
        The execution context to have globals added.

    KWArgs:
        @overwrite
        When true, apply the globals even if there is a value already in place.
        Defaults to False.
    """
    for key in defaults:
        # if the key is present and not being ovewritten, continue the loop
        if exec_context.has(key) and (not overwrite): continue
        # otherwise, apply the default value
        exec_context.set(key,defaults[key])
