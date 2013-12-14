#!/usr/bin/python

import os, tempfile, shutil

class ScratchContainer(object):
    def setUp(self):
        self.scratch_dir = tempfile.mkdtemp()
    def tearDown(self):
        shutil.rmtree(self.scratch_dir)

    def get_backup_path(self,backup_dir,relpath):
        return os.path.join(self.scratch_dir,backup_dir,
            os.path.relpath(self.scratch_dir,'/'),relpath)

    def make_dir(self,relpath):
        full_path = os.path.join(self.scratch_dir,relpath)
        if not os.path.exists(full_path):
            os.makedirs(full_path)

    def write_file(self,relpath,content):
        with open(os.path.join(self.scratch_dir,relpath),'w') as f:
            f.write(content)

    def read_file(self,relpath):
        with open(os.path.join(self.scratch_dir,relpath),'r') as f:
            return f.read()

    def get_file_mode(self,relpath):
        return os.stat(os.path.join(self.scratch_dir,relpath)).st_mode\
               & 0777
