#!/usr/bin/python

import os

import src.execute.action as action
import src.util.locations as locations
import src.util.ugo as ugo

from src.block.base_block import Block, BlockException

class FileBlock(Block):
    """
    A file block describes an action performed on a file.
    This includes creation, deletion, and string append.
    """
    def __init__(self):
        Block.__init__(self,Block.types.FILE)

    def expand_file_paths(self,root_dir):
        """
        Expand relative paths in source and target to be absolute paths
        beginning with the SALVE_ROOT.
        """
        if not self.has('target'):
            raise BlockException('FileBlock missing target')

        if not locations.is_abs_or_var(self.get('source')):
            self.set('source', os.path.join(root_dir,
                                            self.get('source')))
        if not locations.is_abs_or_var(self.get('target')):
            self.set('target', os.path.join(root_dir,
                                            self.get('target')))

    def to_action(self):
        def ensure_abspath_attrs(*args):
            self.ensure_has_attrs(*args)
            for arg in args:
                assert os.path.isabs(self.get(arg))
        commands = []
        if self.get('action') == 'copy':
            self.ensure_has_attrs('user','group','mode')
            ensure_abspath_attrs('source','target')
            copy_file = ' '.join(['cp',
                                  self.get('source'),
                                  self.get('target')
                                 ])
            chown_file = ' '.join(['chown',
                                   self.get('user')+':'+\
                                   self.get('group'),
                                   self.get('target')
                                  ])
            chmod_file = ' '.join(['chmod',
                                   self.get('mode'),
                                   self.get('target')
                                  ])
            commands = [copy_file,chmod_file]
            if ugo.is_root(): commands.append(chown_file)
        elif self.get('action') == 'create':
            self.ensure_has_attrs('user','group','mode')
            ensure_abspath_attrs('target')
            touch_file = ' '.join(['touch',
                                   self.get('target'),
                                  ])
            chmod_file = ' '.join(['chmod',
                                   self.get('mode'),
                                   self.get('target')
                                  ])
            chown_file = ' '.join(['chown',
                                   self.get('user')+':'+\
                                   self.get('group'),
                                   self.get('target')
                                  ])
            commands = [touch_file,chmod_file]
            if ugo.is_root(): commands.append(chown_file)
        return action.ShellAction(commands)
