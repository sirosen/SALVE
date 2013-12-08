#!/usr/bin/python

import os

import src.execute.action as action
import src.execute.backup as backup
import src.execute.copy as copy
import src.util.locations as locations
import src.util.ugo as ugo

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
        for attr in ['backup_dir','backup_log','target','user','group',
                     'mode']:
            self.min_attrs.add(attr)

    def _mkdir_action(self,dirname,mode):
        """
        Creates a shell action to create the specified directory with
        the specified mode. Useful throughout dir actions, as handling
        subdirectories correctly often requires more of these.

        Args:
            @dirname
            The path to the directory to be created. Should be an
            absolute path in order to ensure correctness.

            @mode
            The mode (umask) of the directory being created.
        """
        return action.ShellAction('mkdir -p -m %s %s' % (mode,dirname),
                                  self.context)

    def create_action(self):
        """
        Generate a directory creation action. This may be all or part of
        the action produced by the block upon action conversion.
        """
        self.ensure_has_attrs('target','user','group','mode')
        # TODO: replace with exception
        assert os.path.isabs(self.get('target'))
        # create the target dir
        act = self._mkdir_action(self.get('target'),self.get('mode'))

        # if running as root, add a non-recursive chown as well, to
        # set the correct permissions for the directory but not its
        # children
        if ugo.is_root():
            user_group_str = self.get('user')+':'+self.get('group')
            chown_dir = 'chown %s %s' % (user_group_str,self.get('target'))
            chown_dir = action.ShellAction(chown_dir,self.context)
            act = action.ActionList([act,chown_dir],self.context)

        return act

    def copy_action(self):
        """
        Copy a directory. This may be all or part of the action produced
        by the block upon action conversion.
        """
        self.ensure_has_attrs('source','target','user','group','mode')
        # TODO: replace with exception
        assert os.path.isabs(self.get('target'))
        assert os.path.isabs(self.get('source'))

        # create the target directory; make the action an AL for
        # simplicity when adding actions to it
        mkdir = self._mkdir_action(self.get('target'),self.get('mode'))
        act = action.ActionList([mkdir],self.context)

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
                act.append(self._mkdir_action(target_dir,
                                              self.get('mode')))
            # for every file, first backup any file that is at the
            # destination, then copy from source to target tree
            for f in files:
                fname = os.path.join(d,f)
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

        # if running as root, recursively apply permissions after the copy
        # TODO: replace with something less heavy handed (i.e. set permissions
        # for everything in the source tree, not the entire dir)
        if ugo.is_root():
            user_group_str = self.get('user')+':'+self.get('group')
            chown_dir = 'chown -R %s %s' % (user_group_str,self.get('target'))
            act.append(action.ShellAction(chown_dir,self.context))

        return act

    def to_action(self):
        def add_action(act,new,prepend=False):
            """
            Defines a uniform way of expanding an action regardless of
            whether or not it is an AL.

            Args:
                @act
                The action being expanded.
                @new
                The action being added to @act

            KWArgs:
                @prepend
                When True, prepend @new to @act. When False, append
                instead.
            """
            # convert @act to an AL if it wasn't one before
            if not isinstance(act,action.ActionList):
                act = action.ActionList([act],self.context)
            if prepend: act.prepend(new)
            else: act.append(new)
            return act

        # only certain actions should actually trigger a dir backup
        # remove does not exist yet, but when it is added, it will
        triggers_backup = ('remove',)
        self.ensure_has_attrs('action')
        if self.get('action') == 'create':
            dir_act = self.create_action()
        elif self.get('action') == 'copy':
            dir_act = self.copy_action()
        else:
            raise self.mk_except('Unsupported directory block action.')

        # if the action is classified as causing a directory backup, the
        # backup action is created and prepended to the existing action
        if self.get('action') in triggers_backup and\
           os.path.exists(self.get('target')):
            # no need to test until 'remove' is defined
            backup_act = backup.DirBackupAction(self.get('target'), #pragma: no cover
                                                self.get('backup_dir'),
                                                self.get('backup_log'),
                                                self.context)

            dir_act = add_action(dir_act,backup_act,prepend=True)

        return dir_act
