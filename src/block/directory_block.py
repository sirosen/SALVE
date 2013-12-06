#!/usr/bin/python

import os

import src.execute.action as action
import src.execute.backup as backup
import src.execute.copy as copy
import src.util.locations as locations
import src.util.ugo as ugo

from src.block.base_block import Block, BlockException

class DirBlock(Block):
    """
    A directory block describes an action performed on a directory.
    This includes creation, deletion, and copying from source.
    """
    def __init__(self,exception_context=None):
        Block.__init__(self,Block.types.DIRECTORY,exception_context)

    def expand_file_paths(self,root_dir):
        """
        Expand relative paths in source and target to be absolute paths
        beginning with the root directory.
        """
        if not self.has('target'):
            raise self.mk_except('DirBlock missing target')

        if not self.has('backup_dir'):
            raise self.mk_except('DirBlock missing backup_dir')

        if not self.has('backup_log'):
            raise self.mk_except('DirBlock missing backup_log')

        if self.has('source') and \
           not locations.is_abs_or_var(self.get('source')):
            self.set('source', os.path.join(root_dir,
                                            self.get('source')))

        if not locations.is_abs_or_var(self.get('backup_dir')):
            self.set('backup_dir', os.path.join(root_dir,
                                                self.get('backup_dir')))
        if not locations.is_abs_or_var(self.get('backup_log')):
            self.set('backup_log', os.path.join(root_dir,
                                                self.get('backup_log')))
        if not locations.is_abs_or_var(self.get('target')):
            self.set('target', os.path.join(root_dir,
                                            self.get('target')))

    def _mkdir_action(self,dirname,user,group,mode):
        mkdir = ' '.join(['mkdir -p -m',mode,dirname])
        commands = [mkdir]
        if ugo.is_root():
            chown_dir = ' '.join(['chown',user+':'+group,dirname])
            commands.append(chown_dir)
        return action.ShellAction(commands,self.context)

    def create_action(self):
        """
        Create a directory. Used by creation and dir copy.
        """
        self.ensure_has_attrs('target','user','group','mode')
        # TODO: replace with exception
        assert os.path.isabs(self.get('target'))
        return self._mkdir_action(self.get('target'),self.get('user'),
                                  self.get('group'),self.get('mode'))

    def copy_action(self):
        """
        Copy a directory.
        """
        self.ensure_has_attrs('source','target','user','group','mode')
        # TODO: replace with exception
        assert os.path.isabs(self.get('target'))
        assert os.path.isabs(self.get('source'))

        mkdir = self._mkdir_action(self.get('target'),self.get('user'),
                                   self.get('group'),self.get('mode'))
        act = action.ActionList([mkdir],self.context)

        sourcelen = len(self.get('source'))
        backup_dir = self.get('backup_dir')
        backup_log = self.get('backup_log')
        for d,subdirs,files in os.walk(self.get('source')):
            for f in files:
                fname = os.path.join(d,f)
                target_dir = os.path.join(
                                self.get('target'),
                                os.path.relpath(d,self.get('source'))
                             )
                target_fname = os.path.join(target_dir,f)
                file_act = action.ActionList([],self.context)
                file_act.append(backup.FileBackupAction(target_fname,
                                                        backup_dir,
                                                        backup_log,
                                                        self.context))
                file_act.append(self._mkdir_action(
                    os.path.dirname(target_fname),self.get('user'),
                    self.get('group'),self.get('mode'))
                    )
                file_act.append(copy.FileCopyAction(fname,
                                                    target_fname,
                                                    self.context))
                act.append(file_act)

        if ugo.is_root():
            chown_dir = ' '.join(['chown -R',self.get('user')+':'+\
                                  self.get('group'),self.get('target')
                                 ])
            act.append(action.ShellAction([chown_dir],self.context))
        return act

    def to_action(self):
        def add_action(act,new,prepend=False):
            if not isinstance(act,action.ActionList):
                act = action.ActionList([act],self.context)
            if prepend: act.prepend(new)
            else: act.append(new)
            return act

        commands = []
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

        if self.get('action') in triggers_backup and\
           os.path.exists(self.get('target')):
            backup_act = backup.DirBackupAction(self.get('target'),
                                                self.get('backup_dir'),
                                                self.get('backup_log'),
                                                self.context)

            dir_act = add_action(dir_act,backup_act,prepend=True)

        return dir_act
