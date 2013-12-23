#!/usr/bin/python

import os

import src.execute.action as action
import src.execute.backup as backup
import src.execute.copy as copy
import src.execute.create as create
import src.execute.modify as modify

from src.block.base import Block, BlockException

class DirBlock(Block):
    """
    A directory block describes an action performed on a directory.
    This includes creation, deletion, and copying from source.
    """
    def __init__(self,context=None):
        """
        Directory Block constructor.

        KWArgs:
            @context
            The StreamContext of the block's initial identifier.
        """
        Block.__init__(self,Block.types.DIRECTORY,context)
        for attr in ['backup_dir','backup_log','target','source']:
            self.path_attrs.add(attr)
        for attr in ['backup_dir','backup_log','target']:
            self.min_attrs.add(attr)

    def _mkdir(self,dirname):
        """
        Creates a shell action to create the specified directory with
        the block's mode if set. Useful throughout dir actions, as
        handling subdirectories correctly often requires more of these.

        Args:
            @dirname
            The path to the directory to be created. Should be an
            absolute path in order to ensure correctness.
        """
        act = create.DirCreateAction(dirname,self.context)
        if self.has('mode'):
            act = action.ActionList([act],self.context)
            act.append(modify.DirChmodAction(dirname,
                                             self.get('mode'),
                                             self.context))
        return act

    def create_action(self):
        """
        Generate a directory creation action. This may be all or part of
        the action produced by the block upon action conversion.
        """
        self.ensure_has_attrs('target')
        # TODO: replace with exception
        assert os.path.isabs(self.get('target'))
        # create the target dir
        act = self._mkdir(self.get('target'))

        # if 'user' and 'group' are set add a non-recursive chown
        # as well, to set the correct permissions for the directory
        # but not its children
        if self.has('user') and self.has('group'):
            if not isinstance(act,action.ActionList):
                act = action.ActionList([act],self.context)
            act.append(modify.DirChownAction(self.get('target'),
                                             self.get('user'),
                                             self.get('group'),
                                             self.context))

        return act

    def copy_action(self):
        """
        Copy a directory. This may be all or part of the action produced
        by the block upon action conversion.
        """
        self.ensure_has_attrs('source','target')
        # TODO: replace with exception
        assert os.path.isabs(self.get('target'))
        assert os.path.isabs(self.get('source'))

        # create the target directory; make the action an AL for
        # simplicity when adding actions to it
        act = self._mkdir(self.get('target'))
        if not isinstance(act,action.ActionList):
            act = action.ActionList([act],self.context)

        backup_dir = self.get('backup_dir')
        backup_log = self.get('backup_log')
        # walk over all files and subdirs in the directory, creating
        # directories and copying files
        for d,subdirs,files in os.walk(self.get('source')):
            # for every subdir, rewrite it to be prefixed with the
            # target and create that directory
            for sd in subdirs:
                target_dir = os.path.join(
                                self.get('target'),
                                os.path.relpath(os.path.join(d,sd),
                                                self.get('source'))
                             )
                act.append(self._mkdir(target_dir))
            # for every file, first backup any file that is at the
            # destination, then copy from source to target tree
            for f in files:
                fname = os.path.join(d,f)
                target_dir = os.path.join(
                                self.get('target'),
                                os.path.relpath(d,self.get('source'))
                             )
                target_fname = os.path.join(target_dir,f)
                backup_act = backup.FileBackupAction(target_fname,
                                                     backup_dir,
                                                     backup_log,
                                                     self.context)
                copy_act = copy.FileCopyAction(fname,
                                               target_fname,
                                               self.context)
                file_act = action.ActionList([backup_act,copy_act],self.context)
                act.append(file_act)

        if self.has('mode'):
            act.append(modify.DirChmodAction(self.get('target'),
                                             self.get('mode'),
                                             self.context,
                                             recursive=True))

        # if 'user' and 'group' are set, recursively apply permissions
        # after the copy
        # TODO: replace with something less heavy handed (i.e. set
        # permissions for everything in the source tree, not the entire
        # dir)
        if self.has('user') and self.has('group'):
            chown_dir = modify.DirChownAction(self.get('target'),
                                              self.get('user'),
                                              self.get('group'),
                                              self.context,
                                              recursive=True)
            act.append(chown_dir)

        return act

    def to_action(self):
        """
        Uses the DirectoryBlock to produce an action.
        The type of action produced depends on the value of the block's
        'action' attribute.
        If it is a create action, this boils down to an invocation of
        'mkdir -p'. If it is a copy action, this is a recursive
        directory copy that creates the target directories and backs up
        any files that are being overwritten.
        """
        # only certain actions should actually trigger a dir backup
        # remove does not exist yet, but when it is added, it will
        self.ensure_has_attrs('action')
        if self.get('action') == 'create':
            dir_act = self.create_action()
        elif self.get('action') == 'copy':
            dir_act = self.copy_action()
        else:
            raise self.mk_except('Unsupported DirectoryBlock action.')

        return dir_act
