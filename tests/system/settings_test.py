import os
import textwrap
import logging
from nose.tools import istest

import salve
from tests import system


class TestWithRunLog(system.RunScratchContainer):
    default_settings_content = textwrap.dedent(
        """
        [global]
        backup_dir=$HOME/backups
        backup_log=$HOME/backup.log

        log_level=DEBUG
        run_log=$HOME/run_log

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
        System: Settings, Set a Run Log File

        Runs a manifest with settings which set a run log and verifies that
        the error, warn, and info output is written to the log.
        """
        content = 'file { action copy source 1.man target 2.man }\n'
        self.write_file('1.man', content)
        self.run_on_manifest('1.man')
        assert self.exists('2.man')
        s = self.read_file('2.man')
        assert s == content
        s = self.read_file(os.path.join(self.userhome, 'run_log'))
        assert len(s) > 0

    @istest
    def command_line_log_level(self):
        """
        System: Settings, Set Log Level in Command Line

        Runs a manifest with settings that set the log level, and verifies that
        the log level set in the command line is the real value used.
        """
        content = 'file { action copy source 1.man target 2.man }\n'
        self.write_file('1.man', content)
        self.run_on_args(['./salve.py', 'deploy', '-m', '1.man',
                          '-l', 'WARNING', '-d', self.scratch_dir])
        assert self.exists('2.man')
        s = self.read_file('2.man')
        assert s == content
        assert salve.logger.level == logging.WARNING
