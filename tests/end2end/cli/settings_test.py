#!/usr/bin/python

import os
import mock
import shlex
import textwrap
from nose.tools import istest

from tests.end2end.cli import common

import salve


class TestWithRunLog(common.RunScratchContainer):
    default_settings_content = textwrap.dedent(
        """
        [global]
        backup_dir=$HOME/backups
        backup_log=$HOME/backup.log

        log_level=ALL
        run_log=$HOME/run_log
        verbosity=3

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

    @istest
    def explicit_run_log(self):
        """
        E2E: Settings, Set a Run Log File

        Runs a manifest with settings which set a run log and verifies that
        the error, warn, and info output is written to the log.
        """
        content = 'file { action copy source 1.man target 2.man }\n'
        self.write_file('1.man', content)
        self.run_on_manifest('1.man')
        assert self.exists('2.man')
        s = self.read_file('2.man')
        assert s == content, '%s' % s
        salve.logger.logfile.flush()
        s = self.read_file(os.path.join(self.userhome, 'run_log'))
        assert len(s) > 0
