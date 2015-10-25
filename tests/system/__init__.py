#!/usr/bin/python

import mock

from salve import cli
from tests.util import scratch


class RunScratchContainer(scratch.ScratchContainer):
    def run_on_args(self, argv):
        with mock.patch('sys.argv', argv):
            return cli.main()

    def run_on_manifest(self, manifest, argv=None):
        man_path = self.get_fullname(manifest)
        arguments = ['./salve.py', 'deploy', '-m', man_path]
        if argv is None:
            arguments += ['-d', self.scratch_dir]
        else:
            arguments += argv
        self.run_on_args(arguments)
