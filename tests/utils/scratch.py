#!/usr/bin/python

import os
import tempfile
import shutil

import mock
import textwrap
import string

import salve.util.locations as locations

from tests.utils import MockedGlobals


class ScratchContainer(MockedGlobals):
    default_settings_content = textwrap.dedent(
        """
        [global]
        backup_dir=$HOME/backups
        backup_log=$HOME/backup.log

        log_level=ALL
        # run_log=$HOME/.salve/run_log

        [default]
        user=$USER # an inline comment
        group=$SALVE_USER_PRIMARY_GROUP'

        [file]
        action=copy
        mode=600

        [directory]
        action=copy
        mode=755

        [manifest]
        """
    )

    def __init__(self):
        MockedGlobals.__init__(self)

        self.patches = set()
        self.scratch_dir = tempfile.mkdtemp()

        mock_env = {
            'SUDO_USER': 'user1',
            'USER': 'user1',
            'HOME': self.get_fullname('home/user1')
        }
        self.username = 'user1'
        self.sudouser = 'user1'
        self.userhome = 'home/user1'
        os.makedirs(mock_env['HOME'])
        self.patches.add(mock.patch.dict('os.environ', mock_env))

        def get_groupname(user):
            if user == 'user1':
                return 'group1'
            else:
                return 'nogroup'

        real_expanduser = os.path.expanduser

        def expanduser(path):
            if path.strip() == '~user1':
                return mock_env['HOME']
            else:
                return real_expanduser(path)

        settings_loc = os.path.join(mock_env['HOME'], 'settings.ini')
        self.write_file(settings_loc, self.default_settings_content)
        real_open = open

        def mock_open(path, *args, **kwargs):
            if os.path.abspath(path) == locations.get_default_config():
                return real_open(settings_loc, *args, **kwargs)
            else:
                return real_open(path, *args, **kwargs)

        self.patches.add(
            mock.patch('salve.util.ugo.get_group_from_username',
                       get_groupname)
            )

        # mock the gid and uid helpers -- this allows dummy user lookups
        # with this mocking in place, the dummy user looks like the real
        # user
        real_uid = os.geteuid()
        real_gid = os.getegid()
        self.patches.add(mock.patch('salve.util.ugo.name_to_uid',
            lambda x: real_uid)
            )
        self.patches.add(mock.patch('salve.util.ugo.name_to_gid',
            lambda x: real_gid)
            )

        self.patches.add(
            mock.patch('os.path.expanduser', expanduser)
            )

        # use the builtins import to check if we are in Py3
        # more foolproof than using sys.version_info
        try:
            import builtins
            self.patches.add(
                mock.patch('builtins.open', mock_open)
                )
        # if it fails with an import error, we are in Py2
        except ImportError:
            import __builtin__ as builtins
            self.patches.add(
                mock.patch('__builtin__.open', mock_open)
                )

    def setUp(self):
        MockedGlobals.setUp(self)
        for p in self.patches:
            p.start()

    def tearDown(self):
        MockedGlobals.tearDown(self)

        def recursive_chmod(d):
            os.chmod(d, 0o777)
            for f in os.listdir(d):
                fullname = os.path.join(d, f)
                if os.path.isdir(fullname) and not os.path.islink(fullname):
                    recursive_chmod(fullname)

        recursive_chmod(self.scratch_dir)
        shutil.rmtree(self.scratch_dir)

        for p in self.patches:
            p.stop()

    def get_backup_path(self, backup_dir):
        return os.path.join(self.get_fullname(backup_dir), 'files')

    def make_dir(self, relpath):
        full_path = self.get_fullname(relpath)
        try:
            os.makedirs(full_path)
        except OSError as e:
            # 'File exists' errno
            if e.errno == 17:
                return
            else:
                raise

    def exists(self, relpath):
        return os.path.exists(self.get_fullname(relpath))

    def listdir(self, relpath):
        return os.listdir(self.get_fullname(relpath))

    def write_file(self, relpath, content):
        with open(self.get_fullname(relpath), 'w') as f:
            f.write(content)

    def read_file(self, relpath):
        filename = os.path.join(self.scratch_dir, relpath)
        with open(filename, 'r') as f:
            return f.read()

    def get_mode(self, relpath):
        return os.stat(self.get_fullname(relpath)).st_mode & 0o777

    def get_fullname(self, relpath):
        return os.path.join(self.scratch_dir, relpath)
