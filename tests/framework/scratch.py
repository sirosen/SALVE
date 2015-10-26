import os
import tempfile
import shutil

import mock
import textwrap

from salve import paths
from tests.framework import MockedGlobals


class ScratchContainer(MockedGlobals):
    default_settings_content = textwrap.dedent(
        """
        [global]
        backup_dir=$HOME/backups
        backup_log=$HOME/backup.log

        log_level=DEBUG
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

    def _inithelper_mockenv(self):
        self.username = 'user1'
        self.userhome = self.get_fullname('home/user1')
        os.makedirs(self.userhome)
        mock_env = {
            'SUDO_USER': self.username,
            'USER': self.username,
            'HOME': self.userhome
        }
        self.patches.add(mock.patch.dict('os.environ', mock_env))

    def _inithelper_mockgroupname(self):
        def get_groupname(user):
            if user == self.username:
                return 'group1'
            else:
                return 'nogroup'

        self.patches.add(mock.patch('salve.ugo.get_group_from_username',
                                    get_groupname))

    def _inithelper_mockexpanduser(self):
        real_expanduser = os.path.expanduser

        def expanduser(path):
            if path.strip() == '~{0}'.format(self.username):
                return self.userhome
            else:
                return real_expanduser(path)

        self.patches.add(mock.patch('os.path.expanduser', expanduser))

    def _inithelper_mocksettings(self):
        settings_loc = os.path.join(self.userhome, 'settings.ini')
        self.write_file(settings_loc, self.default_settings_content)

        real_open = open

        def mock_open(path, *args, **kwargs):
            if os.path.abspath(path) == paths.get_default_config():
                return real_open(settings_loc, *args, **kwargs)
            else:
                return real_open(path, *args, **kwargs)

        # use the builtins import to check if we are in Py3
        # more foolproof than using sys.version_info because it will work even
        # on unexpected python versions as long as the builtins module doesn't
        # get renamed again
        try:  # flake8: noqa
            import builtins
            self.patches.add(mock.patch('builtins.open', mock_open))
        # if it fails with an import error, we are in Py2
        except ImportError:  # flake8: noqa
            import __builtin__ as builtins
            self.patches.add(mock.patch('__builtin__.open', mock_open))

    def __init__(self):
        MockedGlobals.__init__(self)
        self.scratch_dir = tempfile.mkdtemp()

        self._inithelper_mockenv()
        self._inithelper_mockgroupname()
        self._inithelper_mockexpanduser()
        self._inithelper_mocksettings()

        # mock the gid and uid helpers -- this allows dummy user lookups
        # with this mocking in place, the dummy user looks like the real
        # user
        self.patches.add(mock.patch('salve.ugo.name_to_uid',
                                    lambda x: os.geteuid()))
        self.patches.add(mock.patch('salve.ugo.name_to_gid',
                                    lambda x: os.getegid()))

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
