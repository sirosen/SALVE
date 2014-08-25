#!/usr/bin/python

import subprocess

import salve

from salve.action import Action, ActionException
from salve.context import ExecutionContext


class ShellAction(Action):
    """
    A ShellAction is one of the basic Action types, used to invoke
    shell subprocesses.
    """
    def __init__(self, command, file_context):
        """
        ShellAction constructor.

        Args:
            @command
            A string that defines the shell command to execute when the
            ShellAction is invoked.
            @file_context
            The FileContext.
        """
        Action.__init__(self, file_context)
        self.cmd = command

    def __str__(self):
        return 'ShellAction(' + str(self.cmd) + ')'

    def execute(self, filesys):
        """
        ShellAction execution.

        Invokes the ShellAction's command, and fails if it returns a
        nonzero exit code, and returns its stdout and stderr.
        """
        # transition to the execution phase
        salve.exec_context.transition(ExecutionContext.phases.EXECUTION)

        # run the command, passing output to PIPE
        process = subprocess.Popen(self.cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True)
        # Popen is asynchronous without an invocation of wait()
        process.wait()
        # check if returncode became nonzero, and fail if it did
        if process.returncode != 0:
            raise ActionException(str(self) +
                ' failed with exit code ' + str(process.returncode),
                self.file_context)

        return process.communicate()
