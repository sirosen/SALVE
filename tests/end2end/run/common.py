#!/usr/bin/python

import mock

import tests.utils.scratch
import src.run.command

class RunScratchContainer(tests.utils.scratch.ScratchContainer):
    def run_on_args(self,argv):
        with mock.patch('sys.argv',argv):
            return src.run.command.run()

    def run_on_manifest(self,manifest):
        man_path = self.get_fullname(manifest)
        argv = ['./salve.py','deploy','-m',man_path,
                '-d',self.scratch_dir]
        self.run_on_args(argv)
