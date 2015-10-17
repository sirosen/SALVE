import os
import mock
from nose.tools import istest

from tests.util import ensure_except, scratch

from salve import action
from salve.context import ExecutionContext
from salve.action import backup, create, modify, copy
from salve.exceptions import BlockException

from salve.block import FileBlock

from tests.unit.block import dummy_file_context, dummy_logger, \
    ScratchWithExecCtx


class TestWithScratchdir(ScratchWithExecCtx):
    @istest
    def file_copy_compile(self):
        """
        Unit: File Block Copy Compile
        Verifies the result of converting a file copy block to an action.
        """
        b = FileBlock(dummy_file_context)
        b['action'] = 'copy'
        b['source'] = '/a/b/c'
        b['target'] = '/p/q/r'
        b['user'] = 'user1'
        b['group'] = 'nogroup'
        b['mode'] = '600'

        with mock.patch('salve.logger', dummy_logger):
            act = b.compile()

        assert isinstance(act, action.ActionList)
        assert len(act.actions) == 4
        backup_act = act.actions[0]
        copy_act = act.actions[1]
        mod_act1 = act.actions[2]
        mod_act2 = act.actions[3]

        if isinstance(mod_act1, modify.FileChmodAction):
            chmod_act = mod_act1
            chown_act = mod_act2
        else:
            chown_act = mod_act1
            chmod_act = mod_act2

        assert isinstance(backup_act, backup.FileBackupAction)
        assert isinstance(copy_act, copy.FileCopyAction)
        assert isinstance(chmod_act, modify.FileChmodAction)
        assert isinstance(chown_act, modify.FileChownAction)

        assert backup_act.backup_dir == '/m/n', backup_act.backup_dir
        assert backup_act.logfile == '/m/n.log', backup_act.logfile
        assert copy_act.src == '/a/b/c'
        assert copy_act.dst == '/p/q/r'
        assert '{0:o}'.format(chmod_act.mode) == '600'
        assert chmod_act.target == copy_act.dst
        assert chown_act.user == 'user1'
        assert chown_act.group == 'nogroup'
        assert chown_act.target == copy_act.dst

    @istest
    def file_create_compile(self):
        """
        Unit: File Block Create Compile
        Verifies the result of converting a file create block to an action.
        """
        b = FileBlock(dummy_file_context)
        b['action'] = 'create'
        b['target'] = '/p/q/r'
        b['user'] = 'user1'
        b['group'] = 'nogroup'
        b['mode'] = '0600'
        with mock.patch('os.path.exists', lambda f: True):
            with mock.patch('salve.ugo.is_root', lambda: False):
                with mock.patch('salve.logger', dummy_logger):
                    file_act = b.compile()

        assert isinstance(file_act, action.ActionList)
        assert len(file_act.actions) == 3

        touch = file_act.actions[0]

        mod_act1 = file_act.actions[1]
        mod_act2 = file_act.actions[2]

        if isinstance(mod_act1, modify.FileChmodAction):
            chmod_act = mod_act1
            chown_act = mod_act2
        else:
            chown_act = mod_act1
            chmod_act = mod_act2

        assert isinstance(touch, create.FileCreateAction)
        assert isinstance(chmod_act, modify.FileChmodAction)
        assert isinstance(chown_act, modify.FileChownAction)

        assert str(touch.dst) == '/p/q/r'
        assert chmod_act.target == '/p/q/r'
        assert chown_act.user == 'user1'
        assert chown_act.group == 'nogroup'
        assert chown_act.target == str(touch.dst)

    @istest
    def file_copy_nouser(self):
        """
        Unit: File Block Copy Without User Skips Chown
        Verifies that converting a file copy block to an action when the
        user attribute is unset skips the chown subaction, even as root.
        """
        b = FileBlock(dummy_file_context)
        b['action'] = 'copy'
        b['source'] = '/a/b/c'
        b['target'] = '/p/q/r'
        b['group'] = 'nogroup'
        b['mode'] = '0600'

        with mock.patch('salve.ugo.is_root', lambda: True):
            with mock.patch('salve.logger', dummy_logger):
                file_act = b.compile()

        assert isinstance(file_act, action.ActionList)
        assert len(file_act.actions) == 3
        backup_act = file_act.actions[0]
        copy_act = file_act.actions[1]
        chmod_act = file_act.actions[2]
        assert isinstance(backup_act, backup.FileBackupAction)
        assert isinstance(copy_act, copy.FileCopyAction)
        assert isinstance(chmod_act, modify.FileChmodAction)

        assert backup_act.src == '/p/q/r', backup_act.src
        assert backup_act.backup_dir == '/m/n', backup_act.backup_dir
        assert backup_act.logfile == '/m/n.log', backup_act.logfile
        assert copy_act.src == '/a/b/c'
        assert copy_act.dst == '/p/q/r'
        assert '{0:o}'.format(chmod_act.mode) == '600'
        assert chmod_act.target == copy_act.dst

    @istest
    def file_create_nouser(self):
        """
        Unit: File Block Create Without User Skips Chown
        Verifies that converting a file create block to an action when the
        user attribute is unset leaves out the chown.
        """
        b = FileBlock(dummy_file_context)
        b['action'] = 'create'
        b['target'] = '/p/q/r'
        b['group'] = 'nogroup'
        b['mode'] = '0600'

        # skip backup just to generate a simpler action
        with mock.patch('salve.ugo.is_root', lambda: True):
            with mock.patch('os.path.exists', lambda f: False):
                with mock.patch('salve.logger', dummy_logger):
                    file_act = b.compile()

        assert isinstance(file_act, action.ActionList)
        assert len(file_act.actions) == 2
        touch = file_act.actions[0]
        chmod_act = file_act.actions[1]
        assert isinstance(touch, create.FileCreateAction)
        assert isinstance(chmod_act, modify.FileChmodAction)

        assert str(touch.dst) == '/p/q/r'
        assert '{0:o}'.format(chmod_act.mode) == '600'
        assert chmod_act.target == '/p/q/r'

    @istest
    def file_copy_nogroup(self):
        """
        Unit: File Block Copy Without Group Skips Chown
        Verifies that converting a file copy block to an action when the
        group attribute is unset raises a BlockException.
        """
        b = FileBlock(dummy_file_context)
        b['action'] = 'copy'
        b['source'] = '/a/b/c'
        b['target'] = '/p/q/r'
        b['user'] = 'user1'
        b['mode'] = '0600'

        # skip backup just to generate a simpler action
        with mock.patch('salve.ugo.is_root', lambda: True):
            with mock.patch('os.path.exists', lambda f: False):
                with mock.patch('salve.logger', dummy_logger):
                    file_act = b.compile()

        assert isinstance(file_act, action.ActionList)
        assert len(file_act.actions) == 3
        backup_act = file_act.actions[0]
        copy_act = file_act.actions[1]
        chmod_act = file_act.actions[2]
        assert isinstance(backup_act, backup.FileBackupAction)
        assert isinstance(copy_act, copy.FileCopyAction)
        assert isinstance(chmod_act, modify.FileChmodAction)

        assert backup_act.src == '/p/q/r', backup_act.src
        assert backup_act.backup_dir == '/m/n', backup_act.backup_dir
        assert backup_act.logfile == '/m/n.log', backup_act.backup_dir
        assert copy_act.src == '/a/b/c'
        assert copy_act.dst == '/p/q/r'
        assert '{0:o}'.format(chmod_act.mode) == '600'
        assert chmod_act.target == copy_act.dst

    @istest
    def file_create_nogroup(self):
        """
        Unit: File Block Create Without Group Skips Chown
        Verifies that converting a file create block to an action when the
        group attribute is unset raises a BlockException.
        """
        b = FileBlock(dummy_file_context)
        b['action'] = 'create'
        b['target'] = '/p/q/r'
        b['user'] = 'user1'
        b['mode'] = '0600'

        # skip backup just to generate a simpler action
        with mock.patch('salve.ugo.is_root', lambda: True):
            with mock.patch('os.path.exists', lambda f: False):
                with mock.patch('salve.logger', dummy_logger):
                    file_act = b.compile()

        assert isinstance(file_act, action.ActionList)
        assert len(file_act.actions) == 2
        touch = file_act.actions[0]
        chmod_act = file_act.actions[1]
        assert isinstance(touch, create.FileCreateAction)
        assert isinstance(chmod_act, modify.FileChmodAction)

        assert str(touch.dst) == '/p/q/r'
        assert '{0:o}'.format(chmod_act.mode) == '600'
        assert chmod_act.target == '/p/q/r'

    @istest
    def file_copy_nomode(self):
        """
        Unit: File Block Copy Without Mode Skips Chmod
        Verifies that converting a file copy block to an action when the
        mode attribute is unset raises a BlockException.
        """
        b = FileBlock(dummy_file_context)
        b['action'] = 'copy'
        b['source'] = '/a/b/c'
        b['target'] = '/p/q/r'
        b['user'] = 'user1'
        b['group'] = 'nogroup'

        # skip chown, for simplicity
        with mock.patch('salve.ugo.is_root', lambda: False):
            with mock.patch('salve.logger', dummy_logger):
                file_act = b.compile()

        assert isinstance(file_act, action.ActionList)
        assert len(file_act.actions) == 3
        backup_act = file_act.actions[0]
        copy_act = file_act.actions[1]
        chown_act = file_act.actions[2]

        assert isinstance(backup_act, backup.FileBackupAction)
        assert isinstance(copy_act, copy.FileCopyAction)
        assert isinstance(chown_act, modify.FileChownAction)

        assert backup_act.src == '/p/q/r'
        assert backup_act.backup_dir == '/m/n', backup_act.backup_dir
        assert backup_act.logfile == '/m/n.log'
        assert copy_act.src == '/a/b/c'
        assert copy_act.dst == '/p/q/r'
        assert chown_act.user == 'user1'
        assert chown_act.group == 'nogroup'
        assert chown_act.target == copy_act.dst

    @istest
    def file_create_nomode(self):
        """
        Unit: File Block Create Without Mode Skips Chmod
        Verifies that converting a file create block to an action when the
        mode attribute is unset raises a BlockException.
        """
        b = FileBlock(dummy_file_context)
        b['action'] = 'create'
        b['target'] = '/p/q/r'
        b['user'] = 'user1'
        b['group'] = 'nogroup'

        # skip chown and backup just to generate a simpler action
        with mock.patch('salve.ugo.is_root', lambda: False):
            with mock.patch('os.path.exists', lambda f: False):
                with mock.patch('salve.logger', dummy_logger):
                    act = b.compile()

        assert isinstance(act, action.ActionList)
        assert len(act.actions) == 2
        touch = act.actions[0]
        chown = act.actions[1]
        assert isinstance(touch, create.FileCreateAction)
        assert isinstance(chown, modify.FileChownAction)

        assert str(touch.dst) == '/p/q/r'
        assert chown.user == 'user1'
        assert chown.group == 'nogroup'
        assert chown.target == str(touch.dst)

    @istest
    def file_copy_fails_nosource(self):
        """
        Unit: File Block Copy Fails Without Source
        Verifies that converting a file copy block to an action when the
        source attribute is unset raises a BlockException.
        """
        b = FileBlock(dummy_file_context)
        b['action'] = 'copy'
        b['target'] = '/p/q/r'
        b['user'] = 'user1'
        b['group'] = 'nogroup'
        b['mode'] = '0600'

        with mock.patch('salve.logger', dummy_logger):
            ensure_except(BlockException, b.compile)

    @istest
    def file_copy_fails_notarget(self):
        """
        Unit: File Block Copy Compilation Fails Without Target
        Verifies that converting a file copy block to an action when the
        target attribute is unset raises a BlockException.
        """
        b = FileBlock(dummy_file_context)
        b['action'] = 'copy'
        b['source'] = '/a/b/c'
        b['user'] = 'user1'
        b['group'] = 'nogroup'
        b['mode'] = '0600'

        with mock.patch('salve.logger', dummy_logger):
            ensure_except(BlockException, b.compile)

    @istest
    def file_create_fails_notarget(self):
        """
        Unit: File Block Create Compilation Fails Without Target
        Verifies that converting a file create block to an action when the
        target attribute is unset raises a BlockException.
        """
        b = FileBlock(dummy_file_context)
        b['action'] = 'create'
        b['source'] = '/a/b/c'
        b['user'] = 'user1'
        b['group'] = 'nogroup'
        b['mode'] = '0600'

        with mock.patch('salve.logger', dummy_logger):
            ensure_except(BlockException, b.compile)

    @istest
    def file_path_expand(self):
        """
        Unit: File Block Path Expand
        Tests the results of expanding relative paths in a File block.
        """
        b = FileBlock(dummy_file_context)
        b['source'] = 'p/q/r/s'
        b['target'] = 't/u/v/w/x/y/z/1/2/3/../3'
        root_dir = 'file/root/directory'
        b.expand_file_paths(root_dir)
        source_loc = os.path.join(root_dir, 'p/q/r/s')
        assert b['source'] == source_loc
        target_loc = os.path.join(root_dir, 't/u/v/w/x/y/z/1/2/3/../3')
        assert b['target'] == target_loc

    @istest
    def file_path_expand_fail_notarget(self):
        """
        Unit: File Block Path Expand Fails Without Target
        Verifies that a File Block with the target attribute unset raises
        a BlockException when paths are expanded.
        """
        b = FileBlock(dummy_file_context)
        b['action'] = 'create'
        b['source'] = 'p/q/r/s'
        b['user'] = 'user1'
        b['group'] = 'user1'
        b['mode'] = '644'
        root_dir = 'file/root/directory'
        ensure_except(BlockException, b.expand_file_paths, root_dir)
