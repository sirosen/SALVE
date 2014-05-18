#!/usr/bin/python

from __future__ import print_function

import sys

from src.util.enum import Enum

log_types = Enum('INFO','WARN','ERROR')

def salve_log(message,log_type,context,print_context=True,min_verbosity=0):
    """
    Print a message if the appropriate logging level is set, including
    message info about context and log type.

    Args:
        @message
        A string to print.
        @log_type
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

        @min_verbosity
        The minimum verbosity for this message to print. If that verbosity
        level is not met, the logging action is a no-op.
    """
    # import takes place here to avoid circular dependency
    from src.util.context import context_types

    assert log_type in log_types
    assert context.has_context(context_types.EXEC)

    ectx = context.exec_context
    assert ectx.has('log_level')
    assert ectx.has('run_log')

    target = context.exec_context.get('run_log')

    # short-circuit our way out of logging if
    # - we are specifying a type not in the enabled log_levels
    # - the message requires a higher verbosity level
    if log_type not in ectx.get('log_level') or \
       min_verbosity > ectx.get('verbosity'):
        return

    # if print_context is true, prepend it to the message with a colon separator
    # otherwise, it will be omitted
    if print_context:
        message = str(context) + ': ' + message

    # construct message prefix
    prefix = '['+log_type+']'
    if min_verbosity > 0:
        prefix = prefix+'['+str(min_verbosity)+']'

    print(prefix + ' ' + message,file=target)

def warn(message,context,print_context=True,min_verbosity=0):
    """
    A lightweight wrapper of salve_log with log_type=WARN

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

        @min_verbosity
        The minimum verbosity for this message to print. If that verbosity
        level is not met, the logging action is a no-op.
    """
    salve_log(message,log_types.WARN,context,
              print_context=print_context,min_verbosity=min_verbosity)

def info(message,context,print_context=True,min_verbosity=0):
    """
    A lightweight wrapper of salve_log with log_type=INFO

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

        @min_verbosity
        The minimum verbosity for this message to print. If that verbosity
        level is not met, the logging action is a no-op.
    """
    salve_log(message,log_types.INFO,context,
              print_context=print_context,min_verbosity=min_verbosity)

def error(message,context,print_context=True,min_verbosity=0):
    """
    A lightweight wrapper of salve_log with log_type=ERROR

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

        @min_verbosity
        The minimum verbosity for this message to print. If that verbosity
        level is not met, the logging action is a no-op.
    """
    salve_log(message,log_types.ERROR,context,
              print_context=print_context,min_verbosity=min_verbosity)
