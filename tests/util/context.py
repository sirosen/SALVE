#!/usr/bin/python

from salve.context import ExecutionContext


def clear_exec_context():
    """
    Ensure that there is no current ExecutionContext
    """
    try:
        del ExecutionContext._instance
    except AttributeError:
        pass
