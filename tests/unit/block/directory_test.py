import os
import mock
from nose.tools import istest

from tests.util import ensure_except

from salve import action
from salve.action import backup, modify, create, copy
from salve.exceptions import BlockException

from salve.block import DirBlock

from tests.unit.block import dummy_file_context, dummy_logger, \
    ScratchWithExecCtx


class TestWithScratchdir(ScratchWithExecCtx):
    @istest
    def dir_create_compile(self):
        """
        Unit: Directory Block Create Compile
        Verifies the result of converting a Dir Block to an Action.
        """
        b = DirBlock(dummy_file_context)
        b['action'] = 'create'
        b['target'] = '/p/q/r'
        b['user'] = 'user1'
        b['group'] = 'nogroup'

        with mock.patch('salve.logger', dummy_logger):
            act = b.compile()

        assert isinstance(act, action.ActionList)
        assert len(act.actions) == 2

        mkdir = act.actions[0]
        chown = act.actions[1]
        assert isinstance(mkdir, create.DirCreateAction)
        assert isinstance(chown, modify.DirChownAction)

        assert str(mkdir.dst) == '/p/q/r'
        assert chown.user == 'user1'
        assert chown.group == 'nogroup'
        assert chown.target == str(mkdir.dst)

    @istest
    def dir_create_compile_chmod(self):
        """
        Unit: Directory Block Create Compile With Chmod
        Verifies the result of converting a Dir Block to an Action when the
        Block's mode is set.
        """
        b = DirBlock(dummy_file_context)
        b['action'] = 'create'
        b['target'] = '/p/q/r'
        b['user'] = 'user1'
        b['group'] = 'nogroup'
        b['mode'] = '755'

        with mock.patch('salve.logger', dummy_logger):
            dir_act = b.compile()

        assert isinstance(dir_act, action.ActionList)
        assert len(dir_act.actions) == 3

        mkdir = dir_act.actions[0]
        chmod = dir_act.actions[1]
        chown = dir_act.actions[2]
        assert isinstance(mkdir, create.DirCreateAction)
        assert isinstance(chmod, modify.DirChmodAction)
        assert isinstance(chown, modify.DirChownAction)

        assert str(mkdir.dst) == '/p/q/r'
        assert chmod.target == str(mkdir.dst)
        assert chmod.mode == int('755', 8)
        assert chown.user == 'user1'
        assert chown.group == 'nogroup'
        assert chown.target == str(mkdir.dst)

    @istest
    def dir_create_chown_as_root(self):
        """
        Unit: Directory Block Create Compile With Chown
        Verifies the result of converting a Dir Block to an Action when the
        user is root and the Block's user and group are set.
        """
        b = DirBlock(dummy_file_context)
        b['action'] = 'create'
        b['target'] = '/p/q/r'
        b['user'] = 'user1'
        b['group'] = 'nogroup'
        with mock.patch('salve.ugo.is_root', lambda: True):
            with mock.patch('salve.logger', dummy_logger):
                dir_act = b.compile()

        assert isinstance(dir_act, action.ActionList)
        assert len(dir_act.actions) == 2
        mkdir = dir_act.actions[0]
        chown = dir_act.actions[1]

        assert isinstance(mkdir, create.DirCreateAction)
        assert isinstance(chown, modify.DirChownAction)

        assert str(mkdir.dst) == '/p/q/r'
        assert chown.target == '/p/q/r'
        assert chown.user == 'user1'
        assert chown.group == 'nogroup'

    @istest
    def empty_dir_copy_compile(self):
        """
        Unit: Directory Block Copy Compile (Empty Dir)
        Verifies the result of converting a Dir Block to an Action.
        """
        b = DirBlock(dummy_file_context)
        b['action'] = 'copy'
        b['source'] = '/a/b/c'
        b['target'] = '/p/q/r'
        with mock.patch('os.walk', lambda d: []):
            with mock.patch('salve.logger', dummy_logger):
                dir_act = b.compile()

        assert isinstance(dir_act, action.ActionList)
        assert len(dir_act.actions) == 1
        mkdir_act = dir_act.actions[0]

        assert isinstance(mkdir_act, create.DirCreateAction)

        assert str(mkdir_act.dst) == '/p/q/r'

    @istest
    def nested_dir_copy_compile(self):
        """
        Unit: Directory Block Copy Compile (Nested Dirs)
        Verifies the result of converting a Dir Block to an Action.
        """
        def mock_os_walk(dirname):
            return [
                (dirname, ['subdir1', 'subdir2'], ['file1']),
                (os.path.join(dirname, 'subdir1'), ['subdir3'], ['file2']),
                (os.path.join(dirname, 'subdir2'), [], []),
                (os.path.join(dirname, 'subdir1', 'subdir3'), [], ['file3'])
                ]

        # create and compile a directory block which will trigger the mocked
        # os.walk() routine above
        b = DirBlock(dummy_file_context)
        b['action'] = 'copy'
        b['source'] = '/a/b/c'
        b['target'] = '/p/q/r'
        with mock.patch('os.walk', mock_os_walk):
            with mock.patch('salve.logger', dummy_logger):
                dir_act = b.compile()

        # there should be seven component actions in all: four for each of the
        # directories (counting the containing dir) and three for the three
        # files
        assert isinstance(dir_act, action.ActionList)
        assert len(dir_act.actions) == 7

        # this is the expected order of the actions -- we go in order through
        # os.walk() and handle dirs before files to ensure safety
        mkdir_act1 = dir_act.actions[0]
        mkdir_act2 = dir_act.actions[1]
        mkdir_act3 = dir_act.actions[2]
        file_act1 = dir_act.actions[3]
        mkdir_act4 = dir_act.actions[4]
        file_act2 = dir_act.actions[5]
        file_act3 = dir_act.actions[6]

        # check the destinations of the mkdir actions
        assert isinstance(mkdir_act1, create.DirCreateAction)
        assert str(mkdir_act1.dst) == '/p/q/r'
        assert isinstance(mkdir_act2, create.DirCreateAction)
        assert str(mkdir_act2.dst) == '/p/q/r/subdir1'
        assert isinstance(mkdir_act3, create.DirCreateAction)
        assert str(mkdir_act3.dst) == '/p/q/r/subdir2'
        assert isinstance(mkdir_act4, create.DirCreateAction)
        assert str(mkdir_act4.dst) == '/p/q/r/subdir1/subdir3'

        # check that each file action is a length 2 AL: backup+copy
        assert isinstance(file_act1, action.ActionList)
        assert len(file_act1.actions) == 2
        assert isinstance(file_act2, action.ActionList)
        assert len(file_act2.actions) == 2
        assert isinstance(file_act3, action.ActionList)
        assert len(file_act3.actions) == 2

        # pick apart the file ALs
        backup_act1 = file_act1.actions[0]
        backup_act2 = file_act2.actions[0]
        backup_act3 = file_act3.actions[0]
        file_copy_act1 = file_act1.actions[1]
        file_copy_act2 = file_act2.actions[1]
        file_copy_act3 = file_act3.actions[1]

        # check the backup actions
        assert isinstance(backup_act1, backup.FileBackupAction)
        assert backup_act1.src == '/p/q/r/file1'
        assert isinstance(backup_act2, backup.FileBackupAction)
        assert backup_act2.src == '/p/q/r/subdir1/file2'
        assert isinstance(backup_act3, backup.FileBackupAction)
        assert backup_act3.src == '/p/q/r/subdir1/subdir3/file3'

        # check the file copy actions
        assert isinstance(file_copy_act1, copy.FileCopyAction)
        assert file_copy_act1.src == '/a/b/c/file1'
        assert file_copy_act1.dst == '/p/q/r/file1'
        assert isinstance(file_copy_act2, copy.FileCopyAction)
        assert file_copy_act2.src == '/a/b/c/subdir1/file2'
        assert file_copy_act2.dst == '/p/q/r/subdir1/file2'
        assert isinstance(file_copy_act3, copy.FileCopyAction)
        assert file_copy_act3.src == '/a/b/c/subdir1/subdir3/file3'
        assert file_copy_act3.dst == '/p/q/r/subdir1/subdir3/file3'

    @istest
    def dir_copy_chown_as_root(self):
        """
        Unit: Directory Block Copy Compile (As Root)
        Verifies the result of converting a Dir Block to an Action.
        """
        b = DirBlock(dummy_file_context)
        b['action'] = 'copy'
        b['source'] = '/a/b/c'
        b['target'] = '/p/q/r'
        b['user'] = 'user1'
        b['group'] = 'nogroup'

        with mock.patch('salve.ugo.is_root', lambda: True):
            with mock.patch('os.walk', lambda d: []):
                with mock.patch('salve.logger', dummy_logger):
                    al = b.compile()

        assert isinstance(al, action.ActionList)
        assert len(al.actions) == 2
        mkdir_act = al.actions[0]
        chown_act = al.actions[1]

        assert isinstance(mkdir_act, create.DirCreateAction)
        assert isinstance(chown_act, modify.DirChownAction)

        assert str(mkdir_act.dst) == '/p/q/r'
        assert chown_act.target == '/p/q/r'
        assert chown_act.user == 'user1'
        assert chown_act.group == 'nogroup'

    @istest
    def dir_copy_fails_nosource(self):
        """
        Unit: Directory Block Copy Fails Without Source
        Verifies that converting a Dir Block to an Action raises a
        BlockException.
        """
        b = DirBlock(dummy_file_context)
        b['action'] = 'copy'
        b['target'] = '/p/q/r'
        b['user'] = 'user1'
        b['group'] = 'nogroup'
        b['mode'] = '755'

        with mock.patch('salve.logger', dummy_logger):
            ensure_except(BlockException, b.compile)

    @istest
    def dir_copy_fails_notarget(self):
        """
        Unit: Directory Block Copy Compilation Fails Without Target
        Verifies that converting a Dir Block to an Action raises a
        BlockException.
        """
        b = DirBlock(dummy_file_context)
        b['action'] = 'copy'
        b['source'] = '/a/b/c'
        b['user'] = 'user1'
        b['group'] = 'nogroup'
        b['mode'] = '755'

        with mock.patch('salve.logger', dummy_logger):
            ensure_except(BlockException, b.compile)

    @istest
    def dir_create_fails_notarget(self):
        """
        Unit: Directory Block Create Compilation Fails Without Target
        Verifies that converting a Dir Block to an Action raises a
        BlockException.
        """
        b = DirBlock(dummy_file_context)
        b['action'] = 'create'
        b['user'] = 'user1'
        b['group'] = 'nogroup'
        b['mode'] = '755'

        with mock.patch('salve.logger', dummy_logger):
            ensure_except(BlockException, b.compile)

    @istest
    def dir_path_expand(self):
        """
        Unit: Directory Block Path Expand
        Verifies the results of path expansion in a Dir block.
        """
        b = DirBlock(dummy_file_context)
        b['source'] = 'p/q/r/s'
        b['target'] = 't/u/v/w/x/y/z/1/2/3/../3'
        root_dir = 'file/root/directory'
        b.expand_file_paths(root_dir)
        source_loc = os.path.join(root_dir, 'p/q/r/s')
        assert b['source'] == source_loc
        target_loc = os.path.join(root_dir, 't/u/v/w/x/y/z/1/2/3/../3')
        assert b['target'] == target_loc

    @istest
    def dir_path_expand_fail_notarget(self):
        """
        Unit: Directory Block Path Expand Fails Without Target
        Verifies that path expansion fails when there is no "target"
        attribute.
        """
        # check that this is the case for a "create" action
        b1 = DirBlock(dummy_file_context)
        b1['action'] = 'create'
        b1['user'] = 'user1'
        b1['group'] = 'user1'
        b1['mode'] = '755'
        root_dir = 'file/root/directory'
        ensure_except(BlockException, b1.expand_file_paths, root_dir)

        # check that it also holds for a "copy" action with source set
        b2 = DirBlock(dummy_file_context)
        b2['action'] = 'copy'
        b2['user'] = 'user1'
        b2['group'] = 'user1'
        b2['mode'] = '755'
        b2['source'] = 'p/q/r/s'
        root_dir = 'file/root/directory'
        ensure_except(BlockException, b2.expand_file_paths, root_dir)

    @istest
    def dir_compile_fail_noaction(self):
        """
        Unit: Directory Block Compilation Fails Without Action
        Verifies that block to action conversion fails when there is no
        "action" attribute.
        """
        b = DirBlock(dummy_file_context)
        b['source'] = '/a/b/c'
        b['target'] = '/p/q/r'
        b['user'] = 'user1'
        b['group'] = 'nogroup'
        b['mode'] = '755'

        with mock.patch('salve.logger', dummy_logger):
            ensure_except(BlockException, b.compile)

    @istest
    def dir_compile_fail_unknown_action(self):
        """
        Unit: Directory Block Compilation Fails Unknown Action
        Verifies that block to action conversion fails when the "action"
        attribute has an unrecognized value.
        """
        b = DirBlock(dummy_file_context)
        b['action'] = 'UNDEFINED_ACTION'
        b['source'] = '/a/b/c'
        b['target'] = '/p/q/r'
        b['user'] = 'user1'
        b['group'] = 'nogroup'
        b['mode'] = '755'

        with mock.patch('salve.logger', dummy_logger):
            ensure_except(BlockException, b.compile)
