#!/usr/bin/python

import os

import src.execute.action as action
import src.execute.backup as backup
import src.execute.copy as copy
import src.execute.modify as modify
import src.util.ugo as ugo

from src.block.base import Block, BlockException

class FileBlock(Block):
    """
    A file block describes an action performed on a file.
    This includes creation, deletion, and string append.
    """
    def __init__(self,context=None):
        """
        File Block constructor

        KWArgs:
            @context
            This is a StreamContext identifying the location of the file
            block's identifier, for error reporting.
        """
        Block.__init__(self,Block.types.FILE,context)
        for attr in ['backup_dir','backup_log','target','source']:
            self.path_attrs.add(attr)
        for attr in ['backup_dir','backup_log','target']:
            self.min_attrs.add(attr)

    def to_action(self):
        self.ensure_has_attrs('action')

        def ensure_abspath_attrs(*args):
            self.ensure_has_attrs(*args)
            for arg in args:
                assert os.path.isabs(self.get(arg))

        def add_action(file_act,new,prepend=False):
            if isinstance(file_act,action.ActionList):
                if prepend: file_act.prepend(new)
                else: file_act.append(new)
                return file_act
            else:
                if prepend: acts = [new,file_act]
                else: acts = [file_act,new]
                return action.ActionList(acts,self.context)

        # the following actions trigger backups
        triggers_backup = ('copy',)

        file_action = None
        if self.get('action') == 'copy':
            ensure_abspath_attrs('source','target')
            file_action = copy.FileCopyAction(self.get('source'),
                                              self.get('target'),
                                              self.context)
        elif self.get('action') == 'create':
            ensure_abspath_attrs('target')
            touch_file = ' '.join(['touch','-a',
                                   self.get('target'),
                                  ])
            file_action = action.ShellAction(touch_file,self.context)

        if self.has('mode'):
            chmod = modify.FileChmodAction(self.get('target'),
                                           self.get('mode'),
                                           self.context)
            file_action = add_action(file_action,chmod)

        if ugo.is_root() and self.has('user') and self.has('group'):
            chown = modify.FileChownAction(self.get('target'),
                                           self.get('user'),
                                           self.get('group'),
                                           self.context)
            file_action = add_action(file_action,chown)

        if self.get('action') in triggers_backup and\
           os.path.exists(self.get('target')):
            backup_action = backup.FileBackupAction(
                self.get('target'),
                self.get('backup_dir'),
                self.get('backup_log'),
                self.context)
            file_action = add_action(file_action,
                                     backup_action,
                                     prepend=True)

        return file_action
