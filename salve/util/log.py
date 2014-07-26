#!/usr/bin/python

from __future__ import print_function

import sys

from salve.util.enum import Enum

# check if unicode is defined
try:  # pragma: no cover
    unicode
# if it isn't, we're in Py3, so define it as str
except:  # pragma: no cover
    unicode = str


class Logger(object):
    """
    A Logger is an object to handle output to stderr or a logfile. It writes
    all types of output: informational messages, warnings, and errors, in a
    generic way.

    Allows plugin code which is not aware of the stateful nature of SALVE
    execution to hook into the existing logging infrastructure.
    """
    log_types = Enum('INFO', 'WARN', 'ERROR')

    def __init__(self, exec_context, logfile=sys.stderr):
        """
        Initialize a new logger. Needs a context for printing, and a file-like
        object to write the log messages to.

        Args:
            @exec_context
            An Execution Context which tracks the state of SALVE.

        KWArgs:
            @logfile
            A file-like object to which the logger should write it's output.
            Defaults to stderr, which typically means write to a console.
        """
        self.logfile = logfile
        self.exec_context = exec_context

    def log(self, log_type, message, file_context=None,
            hide_context=False, min_verbosity=0):
        """
        Print a message if the appropriate logging level is set, including
        message info about context and log type.

        Args:
            @message
            A string to print.
            @log_type
            The log_type for the message.

        KWArgs:
            @file_context
            A FileContext which contextualizes the logging.

            @hide_context
            A boolean used to decide whether or not to include the context
            in the message. Defaults to False, but useful for cases in which
            the context is not relevant or the caller wants to alter its
            presentation.

            @min_verbosity
            The minimum verbosity for this message to print. If that verbosity
            level is not met, the logging action is a no-op.
        """
        assert log_type in self.log_types

        ectx = self.exec_context

        # short-circuit our way out of logging if
        # - we are specifying a type not in the enabled log_levels
        # - the message requires a higher verbosity level
        if ectx.has('log_level') and \
           log_type not in ectx.get('log_level'):
            return

        if ectx.has('verbosity'):
            if min_verbosity > ectx.get('verbosity'):
                return
        else:
            if min_verbosity > 0:
                return

        # if hide_context is false, prepend it to the message with
        # a colon separator. Otherwise, it will be omitted
        if not hide_context:
            ctx_prefix = '[' + str(ectx) + '] '
            if file_context is not None:
                ctx_prefix += str(file_context) + ': '

            message = ctx_prefix + message

        # construct message prefix
        ty_prefix = '[' + log_type + ']'
        if min_verbosity > 0:
            ty_prefix = ty_prefix + '[' + str(min_verbosity) + ']'

        # to make every Python happy, make sure "print" is given a string
        print(unicode(ty_prefix + ' ' + message), file=self.logfile)

    def warn(self, *args, **kwargs):
        """
        A lightweight wrapper of log with log_type=WARN
        """
        self.log(self.log_types.WARN, *args, **kwargs)

    def info(self, *args, **kwargs):
        """
        A lightweight wrapper of log with log_type=INFO
        """
        self.log(self.log_types.INFO, *args, **kwargs)

    def error(self, *args, **kwargs):
        """
        A lightweight wrapper of log with log_type=ERROR
        """
        self.log(self.log_types.ERROR, *args, **kwargs)

    def change_logfile(self, logfile):
        """
        Switch the target of all logging.

        Args:
            @logfile
            A file descriptor or other file-like object that is a valid target
            for logging information.
        """
        self.logfile = logfile
