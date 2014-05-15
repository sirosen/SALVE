#!/usr/bin/python

import os
import tempfile
import shutil

import mock
import StringIO
import textwrap

import src.util.locations as locations


class ScratchContainer(object):
    default_settings_content = textwrap.dedent(
        """
        [global]
        backup_dir=$HOME/backups
        backup_log=$HOME/backup.log

        log_level=ERROR
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

    def mock_env(self):
        mock_env = {
            'SUDO_USER': 'user1',
            'USER': 'user1',
            'HOME': self.get_fullname('home/user1')
        }
        os.makedirs(mock_env['HOME'])
        self.patches.add(mock.patch.dict('os.environ',mock_env))

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

        settings_loc = os.path.join(mock_env['HOME'],'settings.ini')
        self.write_file(settings_loc,self.default_settings_content)
        real_open = open
        def mock_open(path,*args,**kwargs):
            if os.path.abspath(path) == locations.get_default_config():
                return real_open(settings_loc,*args,**kwargs)
            else:
                return real_open(path,*args,**kwargs)

        self.patches.add(
            mock.patch('src.util.ugo.get_group_from_username',
                       get_groupname)
            )

        # mock the gid and uid helpers -- this allows dummy user lookups
        # with this mocking in place, the dummy user looks like the real
        # user
        real_uid = os.geteuid()
        real_gid = os.getegid()
        self.patches.add(mock.patch('src.util.ugo.name_to_uid',lambda x: real_uid)
            )
        self.patches.add(mock.patch('src.util.ugo.name_to_gid',lambda x: real_gid)
            )

        self.patches.add(
            mock.patch('os.path.expanduser',expanduser)
            )
        self.patches.add(
            mock.patch('__builtin__.open',mock_open)
            )

    def mock_io(self):
        self.stderr = StringIO.StringIO()
        self.stdout = StringIO.StringIO()

        self.patches.add(
            mock.patch('sys.stderr',self.stderr)
            )
        self.patches.add(
            mock.patch('sys.stdout',self.stdout)
            )

    def setUp(self):
        self.scratch_dir = tempfile.mkdtemp()
        self.patches = set()
        self.mock_env()
        self.mock_io()

        for p in self.patches:
            p.start()

    def tearDown(self):
        def recursive_chmod(dir):
            os.chmod(dir,0777)
            for f in os.listdir(dir):
                fullname = os.path.join(dir,f)
                if os.path.isdir(fullname) and not os.path.islink(fullname):
                    recursive_chmod(fullname)

        recursive_chmod(self.scratch_dir)
        shutil.rmtree(self.scratch_dir)

        for p in self.patches:
            p.stop()

    def get_backup_path(self,backup_dir):
        return os.path.join(self.get_fullname(backup_dir),'files')

    def make_dir(self,relpath):
        full_path = self.get_fullname(relpath)
        # FIXME: should use EAFP style
        if not os.path.exists(full_path):
            os.makedirs(full_path)

    def exists(self,relpath):
        return os.path.exists(self.get_fullname(relpath))

    def listdir(self,relpath):
        return os.listdir(self.get_fullname(relpath))

    def write_file(self,relpath,content):
        with open(self.get_fullname(relpath),'w') as f:
            f.write(content)

    def read_file(self,relpath):
        filename = os.path.join(self.scratch_dir,relpath)
        with open(filename,'r') as f:
            return f.read()

    def get_mode(self,relpath):
        return os.stat(self.get_fullname(relpath)).st_mode & 0777

    def get_fullname(self,relpath):
        return os.path.join(self.scratch_dir,relpath)
