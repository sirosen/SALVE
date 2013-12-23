#!/usr/bin/python

import os, tempfile, shutil
import mock

import src.util.locations as locations


class ScratchContainer(object):
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

        settings_content = (
"""
[common]
backup_dir=$HOME/backups
backup_log=$HOME/backup.log

[file]
action=copy
mode=600
user=$USER
group=$SALVE_USER_PRIMARY_GROUP'

[directory]
action=copy
mode=755
user=$USER
group=$SALVE_USER_PRIMARY_GROUP

[manifest]
"""
        )
        settings_loc = os.path.join(mock_env['HOME'],'settings.ini')
        self.write_file(settings_loc,settings_content)
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
        self.patches.add(
            mock.patch('os.path.expanduser',expanduser)
            )
        self.patches.add(
            mock.patch('__builtin__.open',mock_open)
            )

    def setUp(self):
        self.scratch_dir = tempfile.mkdtemp()
        self.patches = set()
        self.mock_env()

        for p in self.patches:
            p.start()

    def tearDown(self):
        shutil.rmtree(self.scratch_dir)

        for p in self.patches:
            p.stop()

    def get_backup_path(self,backup_dir,relpath):
        return os.path.join(self.scratch_dir,backup_dir,
            os.path.relpath(self.scratch_dir,'/'),relpath)

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
        with open(os.path.join(self.scratch_dir,relpath),'r') as f:
            return f.read()

    def get_file_mode(self,relpath):
        return os.stat(self.get_fullname(relpath)).st_mode\
               & 0777

    def get_fullname(self,relpath):
        return os.path.join(self.scratch_dir,relpath)
