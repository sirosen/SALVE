#!/usr/bin/python

import abc
import os
import sys
import shutil

import salve

from salve import action
from salve import filesys
from salve.util import locations

from salve.util.context import ExecutionContext
from salve.util.six import with_metaclass


class CreateAction(with_metaclass(abc.ABCMeta, action.Action)):
    """
    The base class for all CreateActions.

    Extends verification codes to include UNWRITABLE_TARGET as an error
    condition.
    """
    verification_codes = \
        action.Action.verification_codes.extend('UNWRITABLE_TARGET')


class FileCreateAction(CreateAction):
    """
    An action to create a single file.
    """
    def __init__(self, dst, file_context):
        """
        FileCreateAction constructor.

        Args:
            @dst
            Destination path.
            @file_context
            The FileContext.
        """
        action.Action.__init__(self, file_context)
        self.dst = filesys.real_fs.lookup(dst, elem_type=filesys.File)

    def __str__(self):
        return ("FileCreateAction(dst=" + str(self.dst) +
            ",context=" + repr(self.file_context) + ")")

    def verify_can_exec(self):
        """
        Ensures that the target file exists and is writable, or that
        it does not exist and is in a writable directory.
        """
        # transition to the action verification phase,
        # confirming execution will work
        salve.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        def writable_target():
            """
            Checks if the target is in a writable directory.
            """
            if self.dst.access(os.W_OK):
                return True
            if self.dst.access(os.F_OK):
                return False
            # file is now known not to exist
            assert not self.dst.exists()

            parent = filesys.real_fs.lookup(self.dst.parent_path())
            if parent is not None and parent.access(os.W_OK):
                return True

            # the file is doesn't exist and the containing dir is
            # not writable or doesn't exist
            return False

        salve.logger.info('FileCreate: Checking target is writable, \"%s\"' %
                str(self.dst), file_context=self.file_context,
                min_verbosity=3)

        if not writable_target():
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def execute(self):
        """
        FileCreateAction execution.

        Does a file creation if the file does not exist.
        """
        vcode = self.verify_can_exec()

        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            logstr = ("FileCreate: Non-Writable target file \"%s\""
                    % str(self.dst))
            salve.logger.warn(logstr, file_context=self.file_context)
            return

        # transition to the execution phase
        salve.exec_context.transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing File Creation of \"%s\"' % str(self.dst),
                file_context=self.file_context, min_verbosity=1)

        # touch the file
        self.dst.create()


class DirCreateAction(CreateAction):
    """
    An action to create a directory.
    """
    def __init__(self, dst, file_context):
        """
        DirCreateAction constructor.

        Args:
            @dst
            Destination path.
            @file_context
            The FileContext.
        """
        action.Action.__init__(self, file_context)
        self.dst = filesys.real_fs.lookup(dst, elem_type=filesys.Dir)

    def __str__(self):
        return ("DirCreateAction(dst=" + str(self.dst) + ",context=" +
                repr(self.file_context) + ")")

    def verify_can_exec(self):
        """
        Checks if the target dir already exists, or if its parent is writable.
        """
        # transition to the action verification phase,
        # confirming execution will work
        salve.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        def writable_target():
            """
            Checks if the target is in a writable directory.
            """
            ancestor = locations.get_existing_prefix(str(self.dst))
            ancestor = filesys.real_fs.lookup(ancestor, elem_type=filesys.Dir)
            return ancestor.access(os.W_OK)

        salve.logger.info('DirCreate: Checking if target exists, \"%s\"' %
                str(self.dst), file_context=self.file_context,
                min_verbosity=3)

        # creation of existing dirs is always OK
        if self.dst.exists():
            return self.verification_codes.OK

        salve.logger.info('DirCreate: Checking target is writable, \"%s\"' %
                str(self.dst), file_context=self.file_context,
                min_verbosity=3)

        if not writable_target():
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def execute(self):
        """
        Create a directory and any necessary parents.
        """
        vcode = self.verify_can_exec()

        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            logstr = ("DirCreate: Non-Writable target dir \"%s\"" %
                    str(self.dst))
            salve.logger.warn(logstr, file_context=self.file_context)
            return

        # transition to the execution phase
        salve.exec_context.transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing Directory Creation of \"%s\"'
                % str(self.dst), file_context=self.file_context,
                min_verbosity=1)

        # make the directory
        self.dst.create(recursive=True)
