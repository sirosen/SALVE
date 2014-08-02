#!/usr/bin/python

import os

import salve

from salve import action
from salve.action import backup
from salve.action import copy
from salve.action import create
from salve.action import modify

from salve.block import Block, BlockException


class FileBlock(Block):
    """
    A file block describes an action performed on a file.
    This includes creation, deletion, and string append.
    """
    def __init__(self, file_context):
        """
        File Block constructor

        Args:
            @file_context
            The FileContext for this block.
        """
        Block.__init__(self, Block.types.FILE, file_context)
        for attr in ['target', 'source']:
            self.path_attrs.add(attr)
        for attr in ['target']:
            self.min_attrs.add(attr)
        self.primary_attr = 'target'

    def compile(self):
        """
        Uses the FileBlock to produce an action.
        The type of action produced depends on the value of the block's
        'action' attribute.
        If it is a create action, this boils down to an invocation of
        'touch -a'. If it is a copy action, this is a file copy preceded
        by an attempt to back up the file being overwritten.
        """
        salve.logger.info('Converting FileBlock to FileAction',
                file_context=self.file_context, min_verbosity=3)

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

        def add_action(file_act, new, prepend=False):
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
            if file_act is None:
                return None  # pragma: no cover

            # otherwise, check if the action is an actionlist, and convert
            # it into one if it is not
            if not isinstance(file_act, action.ActionList):
                file_act = action.ActionList([file_act],
                                             self.file_context)
            if prepend:
                file_act.prepend(new)
            else:
                file_act.append(new)
            return file_act

        # the following actions trigger backups
        triggers_backup = ('copy',)

        # set file action to the base action
        file_action = None
        if self.get('action') == 'copy':
            ensure_abspath_attrs('source', 'target')
            file_action = copy.FileCopyAction(self.get('source'),
                                              self.get('target'),
                                              self.file_context)
        elif self.get('action') == 'create':
            ensure_abspath_attrs('target')
            file_action = create.FileCreateAction(self.get('target'),
                                                  self.file_context)
        else:
            raise self.mk_except(
                    'Unsupported FileBlock action.')  # pragma: no cover

        # if 'mode' is set, append a chmod action
        if self.has('mode'):
            chmod = modify.FileChmodAction(self.get('target'),
                                           self.get('mode'),
                                           self.file_context)
            file_action = add_action(file_action, chmod)

        # if 'user' and 'group' are set, append a chwon action
        if self.has('user') and self.has('group'):
            chown = modify.FileChownAction(self.get('target'),
                                           self.get('user'),
                                           self.get('group'),
                                           self.file_context)
            file_action = add_action(file_action, chown)

        # if the action triggers a backup, add a backup action
        if self.get('action') in triggers_backup:
            backup_action = backup.FileBackupAction(
                self.get('target'),
                self.file_context)
            file_action = add_action(file_action,
                                     backup_action,
                                     prepend=True)

        return file_action
