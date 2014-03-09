#!/usr/bin/python

import os

import src.util.log as log
import src.execute.action as action
import src.execute.backup as backup
import src.execute.copy as copy
import src.execute.create as create
import src.execute.modify as modify

from src.block.base import Block, BlockException

class FileBlock(Block):
    """
    A file block describes an action performed on a file.
    This includes creation, deletion, and string append.
    """
    def __init__(self,context):
        """
        File Block constructor

        Args:
            @context
            The SALVEContext for this block.
        """
        assert context.has_context('EXEC')
        Block.__init__(self,Block.types.FILE,context)
        for attr in ['target','source']:
            self.path_attrs.add(attr)
        for attr in ['target']:
            self.min_attrs.add(attr)

    def to_action(self):
        """
        Uses the FileBlock to produce an action.
        The type of action produced depends on the value of the block's
        'action' attribute.
        If it is a create action, this boils down to an invocation of
        'touch -a'. If it is a copy action, this is a file copy preceded
        by an attempt to back up the file being overwritten.
        """
        log.info('Converting FileBlock to FileAction',self.context)

        self.ensure_has_attrs('action')

        def ensure_abspath_attrs(*args):
            """
            A helper method that wraps ensure_has_attrs()
            It additionally ensures that the attribute values are
            absolute paths.

            Args:
                @args
                A variable length argument list of attribute identifiers
                subject to inspection.
            """
            self.ensure_has_attrs(*args)
            for arg in args:
                assert os.path.isabs(self.get(arg))

        def add_action(file_act,new,prepend=False):
            """
            A helper method to merge actions into ALs when it is unknown
            if the original action is an AL. Returns the merged action,
            and makes no guarantees about preserving the originals.

            Args:
                @file_act
                The original action to be extended with @new
                @new
                The action being appended or prepended to @file_act

            KWArgs:
                @prepend
                When True, prepend @new to @file_act. When False, append
                instead.
            """
            # if the action is being skipped, subsequent actions should
            # also be skipped
            if file_act is None: return None

            # otherwise, check if the action is an actionlist, and convert
            # it into one if it is not
            if not isinstance(file_act,action.ActionList):
                file_act = action.ActionList([file_act],
                                             self.context)
            if prepend: file_act.prepend(new)
            else: file_act.append(new)
            return file_act

        # the following actions trigger backups
        triggers_backup = ('copy',)

        # set file action to the base action
        file_action = None
        if self.get('action') == 'copy':
            ensure_abspath_attrs('source','target')
            file_action = copy.FileCopyAction(self.get('source'),
                                              self.get('target'),
                                              self.context)
        elif self.get('action') == 'create':
            ensure_abspath_attrs('target')
            file_action = create.FileCreateAction(self.get('target'),
                                                  self.context)
        else:
            raise self.mk_except('Unsupported FileBlock action.')

        # if 'mode' is set, append a chmod action
        if self.has('mode'):
            chmod = modify.FileChmodAction(self.get('target'),
                                           self.get('mode'),
                                           self.context)
            file_action = add_action(file_action,chmod)

        # if 'user' and 'group' are set, append a chwon action
        if self.has('user') and self.has('group'):
            chown = modify.FileChownAction(self.get('target'),
                                           self.get('user'),
                                           self.get('group'),
                                           self.context)
            file_action = add_action(file_action,chown)

        # if the action triggers a backup, add a backup action
        if self.get('action') in triggers_backup:
            backup_action = backup.FileBackupAction(
                self.get('target'),
                self.context)
            file_action = add_action(file_action,
                                     backup_action,
                                     prepend=True)

        return file_action
