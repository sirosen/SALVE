#!/usr/bin/python

import abc

import salve

from salve import action, paths
from salve.filesys import access_codes
from salve.context import ExecutionContext
from salve.util import with_metaclass


class CopyAction(with_metaclass(abc.ABCMeta, action.Action)):
    """
    The base class for all CopyActions.

    A generic Copy takes a source and destination, and copies the
    source to the destination. The meanings of a Copy vary between
    files and directories, so this is an ABC.
    """
    verification_codes = \
        action.Action.verification_codes.extend('UNWRITABLE_TARGET',
                'UNREADABLE_SOURCE')

    def __init__(self, src, dst, file_context):
        """
        CopyAction constructor.

        Args:
            @src
            The source path (file being copied).
            @dst
            The destination path (being copied to).
            @file_context
            The FileContext.
        """
        action.Action.__init__(self, file_context)
        self.src = src
        self.dst = dst


class FileCopyAction(CopyAction):
    """
    An action to copy a single file.
    """
    def __init__(self, src, dst, file_context):
        """
        FileCopyAction constructor.

        Args:
            @src
            Source path.
            @dst
            Destination path.
            @file_context
            The FileContext.
        """
        CopyAction.__init__(self, src, dst, file_context)

    def __str__(self):
        """
        Stringification into type, source, dst, and context.
        """
        return ("FileCopyAction(src=" + str(self.src) + ",dst=" +
                str(self.dst) + ",context=" + repr(self.file_context) + ")")

    def verify_can_exec(self, filesys):
        """
        Check to ensure that execution can proceed without errors.
        Ensures that the source file exists and is readable, and that
        the target file can be created or is writable.
        """
        # transition to the action verification phase,
        # confirming execution will work
        salve.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        def writable_target():
            """
            Checks if the target file is writable.
            """
            if filesys.access(self.dst, access_codes.W_OK):
                return True
            if filesys.access(self.dst, access_codes.F_OK):
                return False

            # at this point, the file is known not to exist
            # now check properties of the containing dir
            containing_dir = paths.dirname(self.dst)
            if filesys.access(containing_dir, access_codes.W_OK):
                return True

            # if the file doesn't exist, and the dir containing it
            # isn't writable, then the file can't be written
            return False

        def readable_source():
            """
            Checks if the source is a readable file.
            """
            return filesys.access(self.src, access_codes.R_OK)

        def source_islink():
            """
            Checks if the source is a symlink (copied by value, not
            dereferenced)
            """
            return filesys.lookup_type(self.src) is filesys.element_types.LINK

        salve.logger.info('FileCopy: Checking destination is writable, ' +
                '\"%s\"' % self.dst, file_context=self.file_context,
                min_verbosity=3)

        if not writable_target():
            return self.verification_codes.UNWRITABLE_TARGET

        salve.logger.info('FileCopy: Checking if source is link, "%s"' %
                self.src, file_context=self.file_context,
                min_verbosity=3)

        if source_islink():
            return self.verification_codes.OK

        salve.logger.info('FileCopy: Checking source is readable, \"%s\"' %
                self.src, file_context=self.file_context,
                min_verbosity=3)

        if not readable_source():
            return self.verification_codes.UNREADABLE_SOURCE

        return self.verification_codes.OK

    def execute(self, filesys):
        """
        FileCopyAction execution.

        Does a file copy or symlink creation, depending on the type
        of the source file.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            logstr = "FileCopy: Non-Writable target file \"%s\"" % self.dst
            salve.logger.warn(logstr, file_context=self.file_context)
            return

        if vcode == self.verification_codes.UNREADABLE_SOURCE:
            logstr = "FileCopy: Non-Readable source file \"%s\"" % self.src
            salve.logger.warn(logstr, file_context=self.file_context)
            return

        # transition to the execution phase
        salve.exec_context.transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing File Copy \"%s\" -> \"%s\"' %
                (self.src, self.dst), file_context=self.file_context,
                min_verbosity=1)

        filesys.copy(self.src, self.dst)


class DirCopyAction(CopyAction):
    """
    An action to copy a directory tree.
    """
    def __init__(self, src, dst, file_context):
        """
        DirCopyAction constructor.

        Args:
            @src
            Source path.
            @dst
            Destination path.
            @file_context
            The FileContext.
        """
        CopyAction.__init__(self, src, dst, file_context)

    def __str__(self):
        return ("DirCopyAction(src=" + str(self.src) + ",dst=" +
                str(self.dst) + ",context=" + repr(self.file_context) + ")")

    def verify_can_exec(self, filesys):
        """
        Check to ensure that execution can proceed without errors.
        Ensures that the the target directory is writable.
        """
        # transition to the action verification phase,
        # confirming execution will work
        salve.exec_context.transition(ExecutionContext.phases.VERIFICATION)

        def readable_source():
            """
            Checks if the source is a readable and traversable directory. If
            not, then it will be impossible to view and copy its contents.
            """
            return filesys.access(self.src,
                    access_codes.R_OK | access_codes.X_OK)

        def writable_target():
            """
            Checks if the target is in a writable directory.
            """
            return filesys.access(paths.dirname(self.dst),
                    access_codes.W_OK)

        salve.logger.info('DirCopy: Checking source is readable + ' +
                'traversable, \"%s\"' % self.dst,
                file_context=self.file_context, min_verbosity=3)

        if not readable_source():
            return self.verification_codes.UNREADABLE_SOURCE

        salve.logger.info('DirCopy: Checking target is writable, \"%s\"' %
                self.dst, file_context=self.file_context,
                min_verbosity=3)

        if not writable_target():
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def execute(self, filesys):
        """
        Copy a directory tree from one location to another.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.UNREADABLE_SOURCE:
            logstr = "DirCopy: Non-Readable source directory \"%s\"" % self.src
            salve.logger.warn(logstr, file_context=self.file_context)
            return

        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            logstr = "DirCopy: Non-Writable target directory \"%s\"" % self.dst
            salve.logger.warn(logstr, file_context=self.file_context)
            return

        # transition to the execution phase
        salve.exec_context.transition(ExecutionContext.phases.EXECUTION)

        salve.logger.info('Performing Directory Copy \"%s\" -> \"%s\"' %
                (self.src, self.dst), file_context=self.file_context,
                min_verbosity=1)

        filesys.copy(self.src, self.dst)
