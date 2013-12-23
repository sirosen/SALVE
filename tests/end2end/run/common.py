#!/usr/bin/python

import mock

import tests.utils.scratch
import src.run.command

class RunScratchContainer(tests.utils.scratch.ScratchContainer):
    def run_on_args(self,argv):
        with mock.patch('sys.argv',argv):
            return src.run.command.main()

    def run_on_manifest(self,manifest):
        man_path = self.get_fullname(manifest)
        argv = ['./salve.py','-m',man_path,
                '--fileroot',self.scratch_dir]
        self.run_on_args(argv)
