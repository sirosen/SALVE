#!/usr/bin/python

import os

import src.execute.action as action
import src.util.locations as locations

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
        if not self.has('source') or not self.has('target'):
            # TODO: replace with a more informative exception
            raise BlockException('FileBlock missing source or target')

        if not locations.is_abs_or_var(self.get('source')):
            self.set('source', os.path.join(root_dir,
                                            self.get('source')))
        if not locations.is_abs_or_var(self.get('target')):
            self.set('target', os.path.join(root_dir,
                                            self.get('target')))

    def to_action(self):
        # is a no-op if it has already been done
        # otherwise, it ensures that everything will work
        assert os.path.isabs(self.get('source'))
        assert os.path.isabs(self.get('target'))
        if self.get('action') == 'create':
            self.ensure_has_attrs('source','target','user','group',
                                   'mode')
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
            return action.ShellAction([copy_file,chown_file,chmod_file])
        else:
            raise BlockException('Unsupported file block action.')
