#!/usr/bin/python

import os

import src.execute.action as action
import src.execute.backup as backup
import src.util.locations as locations
import src.util.ugo as ugo

from src.block.base_block import Block, BlockException

class DirBlock(Block):
    """
    A directory block describes an action performed on a directory.
    This includes creation, deletion, and copying from source.
    """
    def __init__(self):
        Block.__init__(self,Block.types.DIRECTORY)

    def expand_file_paths(self,root_dir):
        """
        Expand relative paths in source and target to be absolute paths
        beginning with the root directory.
        """
        if not self.has('target'):
            raise BlockException('DirBlock missing target')

        if not self.has('backup_dir'):
            raise BlockException('DirBlock missing backup_dir')

        if not self.has('backup_log'):
            raise BlockException('DirBlock missing backup_log')

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

    def create_commands(self):
        """
        Create a directory. Used by creation and dir copy.
        """
        self.ensure_has_attrs('target','user','group','mode')
        # TODO: replace with exception
        assert os.path.isabs(self.get('target'))
        mkdir = ' '.join(['mkdir -p -m',self.get('mode'),
                          self.get('target')
                         ])
        chown_dir = ' '.join(['chown',self.get('user')+':'+\
                              self.get('group'),self.get('target')
                             ])
        commands = [mkdir]
        if ugo.is_root(): commands.append(chown_dir)
        return commands

    def copy_commands(self):
        """
        Copy a directory.
        """
        self.ensure_has_attrs('source','target','user','group','mode')
        # TODO: replace with exception
        assert os.path.isabs(self.get('target'))
        assert os.path.isabs(self.get('source'))
        mkdir = ' '.join(['mkdir -p -m',self.get('mode'),
                          self.get('target')
                         ])
        copy_dir = ' '.join(['cp -r',
                              os.path.join(self.get('source'),'.'),
                              self.get('target')
                             ])
        chown_dir = ' '.join(['chown -R',self.get('user')+':'+\
                              self.get('group'),self.get('target')
                             ])
        commands = [mkdir,copy_dir]
        if ugo.is_root(): commands.append(chown_dir)
        return commands

    def to_action(self):
        commands = []
        self.ensure_has_attrs('action')
        if self.get('action') == 'create':
            commands = self.create_commands()
        elif self.get('action') == 'copy':
            commands = self.copy_commands()
        else:
            raise BlockException('Unsupported directory block action.')

        dir_act = action.ShellAction(commands)
        if os.path.exists(self.get('target')):
            backup_act = backup.DirBackupAction(self.get('target'),
                                                self.get('backup_dir'),
                                                self.get('backup_log'))

            return action.ActionList([backup_act,dir_act])
        else:
            return dir_act
