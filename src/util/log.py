#!/usr/bin/python

from __future__ import print_function

import sys

from src.util.enum import Enum

log_types = Enum('INFO','WARN','ERROR')

def salve_log(message,type,context,print_context=True):
    """
    Print a message if the appropriate logging level is set, including
    message info about context and log type.

    Args:
        @message
        A string to print.
        @type
        The log_type for the message.
        @context
        A SALVEContext used to find the run_log. If the log
        is not specified in the context, it defaults to stderr.
        Also included in the logging message.

    KWArgs:
        @print_context
        A boolean used to decide whether or not to include the context
        in the message. Defaults to True, but useful for cases in which
        the context is not relevant or the caller wants to alter its
        presentation.
    """
    # import takes place here to avoid circular dependency
    from src.util.context import context_types

    assert type in log_types
    assert context.has_context(context_types.EXEC)

    ectx = context.exec_context

    target = sys.stderr
    if ectx.has('run_log'):
        target = context.exec_context.get('run_log')

    if ectx.has('log_level'):
        # short-circuit our way out of logging if we are specifying a type
        # not in the enabled log_levels
        if type not in ectx.get('log_level'):
            return
    # if log_level is not set, suppress all logging
    else: return

    # if print_context is true, prepend it to the message with a colon separator
    # otherwise, it will be omitted
    if print_context:
        message = str(context) + ': ' + message

    print('['+type+'] ' + message,file=target)

def warn(message,context,print_context=True):
    """
    A lightweight wrapper of salve_log with type=WARN

    Args:
        @message
        A string to print.
        @context
        A SALVEContext used to find the run_log. If the log
        is not specified in the context, it defaults to stderr.
        Also included in the logging message.

    KWArgs:
        @print_context
        A boolean used to decide whether or not to include the context
        in the message. Defaults to True, but useful for cases in which
        the context is not relevant or the caller wants to alter its
        presentation.
    """
    salve_log(message,log_types.WARN,context,print_context=print_context)

def info(message,context,print_context=True):
    """
    A lightweight wrapper of salve_log with type=INFO

    Args:
        @message
        A string to print.
        @context
        A SALVEContext used to find the run_log. If the log
        is not specified in the context, it defaults to stderr.
        Also included in the logging message.

    KWArgs:
        @print_context
        A boolean used to decide whether or not to include the context
        in the message. Defaults to True, but useful for cases in which
        the context is not relevant or the caller wants to alter its
        presentation.
    """
    salve_log(message,log_types.INFO,context,print_context=print_context)

def error(message,context,print_context=True):
    """
    A lightweight wrapper of salve_log with type=ERROR

    Args:
        @message
        A string to print.
        @context
        A SALVEContext used to find the run_log. If the log
        is not specified in the context, it defaults to stderr.
        Also included in the logging message.

    KWArgs:
        @print_context
        A boolean used to decide whether or not to include the context
        in the message. Defaults to True, but useful for cases in which
        the context is not relevant or the caller wants to alter its
        presentation.
    """
    salve_log(message,log_types.ERROR,context,print_context=print_context)
