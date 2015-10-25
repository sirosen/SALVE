#!/usr/bin/python

import os

import salve

from salve.action import ActionList, backup, copy, create, modify
from salve.api import Block

from .base import CoreBlock


class DirBlock(CoreBlock):
    """
    A directory block describes an action performed on a directory.
    This includes creation, deletion, and copying from source.
    """
    def __init__(self, file_context):
        """
        Directory Block constructor.

        Args:
            @file_context
            The FileContext for this block.
        """
        CoreBlock.__init__(self, Block.types.DIRECTORY, file_context)
        for attr in ['target', 'source']:
            self.path_attrs.add(attr)
        for attr in ['target']:
            self.min_attrs.add(attr)
        self.primary_attr = 'target'

    def _mkdir(self, dirname):
        """
        Creates a shell action to create the specified directory with
        the block's mode if set. Useful throughout dir actions, as
        handling subdirectories correctly often requires more of these.

        Args:
            @dirname
            The path to the directory to be created. Should be an
            absolute path in order to ensure correctness.
        """
        act = create.DirCreateAction(dirname, self.file_context)
        if 'mode' in self:
            act = ActionList([act], self.file_context)
            act.append(modify.DirChmodAction(dirname,
                                             self['mode'],
                                             self.file_context))
        return act

    def create_action(self):
        """
        Generate a directory creation action. This may be all or part of
        the action produced by the block upon action conversion.
        """
        self.ensure_has_attrs('target')
        # TODO: replace with exception
        assert os.path.isabs(self['target'])
        # create the target dir
        act = self._mkdir(self['target'])

        # if 'user' and 'group' are set add a non-recursive chown
        # as well, to set the correct permissions for the directory
        # but not its children
        if 'user' in self and 'group' in self:
            if not isinstance(act, ActionList):
                act = ActionList([act], self.file_context)
            act.append(modify.DirChownAction(self['target'],
                                             self['user'],
                                             self['group'],
                                             self.file_context))

        return act

    def copy_action(self):
        """
        Copy a directory. This may be all or part of the action produced
        by the block upon action conversion.
        """
        self.ensure_has_attrs('source', 'target')
        # TODO: replace with exception
        assert os.path.isabs(self['target'])
        assert os.path.isabs(self['source'])

        # create the target directory; make the action an AL for
        # simplicity when adding actions to it
        act = self._mkdir(self['target'])
        if not isinstance(act, ActionList):
            act = ActionList([act], self.file_context)

        # walk over all files and subdirs in the directory, creating
        # directories and copying files
        for d, subdirs, files in os.walk(self['source']):
            # for every subdir, rewrite it to be prefixed with the
            # target and create that directory
            for sd in subdirs:
                target_dir = os.path.join(
                    self['target'],
                    os.path.relpath(os.path.join(d, sd),
                                    self['source'])
                    )
                act.append(self._mkdir(target_dir))
            # for every file, first backup any file that is at the
            # destination, then copy from source to target tree
            for f in files:
                fname = os.path.join(d, f)
                target_dir = os.path.join(
                    self['target'],
                    os.path.relpath(d, self['source'])
                    )
                target_fname = os.path.join(target_dir, f)
                backup_act = backup.FileBackupAction(target_fname,
                                                     self.file_context)
                copy_act = copy.FileCopyAction(fname,
                                               target_fname,
                                               self.file_context)
                file_act = ActionList([backup_act, copy_act],
                                      self.file_context)
                act.append(file_act)

        if 'mode' in self:
            act.append(modify.DirChmodAction(self['target'],
                                             self['mode'],
                                             self.file_context,
                                             recursive=True))

        # if 'user' and 'group' are set, recursively apply permissions
        # after the copy
        # TODO: replace with something less heavy handed (i.e. set
        # permissions for everything in the source tree, not the entire
        # dir)
        if 'user' in self and 'group' in self:
            chown_dir = modify.DirChownAction(self['target'],
                                              self['user'],
                                              self['group'],
                                              self.file_context,
                                              recursive=True)
            act.append(chown_dir)

        return act

    def compile(self):
        """
        Uses the DirectoryBlock to produce an action.
        The type of action produced depends on the value of the block's
        'action' attribute.
        If it is a create action, this boils down to an invocation of
        'mkdir -p'. If it is a copy action, this is a recursive
        directory copy that creates the target directories and backs up
        any files that are being overwritten.
        """
        salve.logger.info(
            '{0}: Converting DirBlock to DirAction'.format(
                str(self.file_context)
                )
            )

        # only certain actions should actually trigger a dir backup
        # remove does not exist yet, but when it is added, it will
        self.ensure_has_attrs('action')
        if self['action'] == 'create':
            dir_act = self.create_action()
        elif self['action'] == 'copy':
            dir_act = self.copy_action()
        else:
            raise self.mk_except('Unsupported DirectoryBlock action.')

        return dir_act
