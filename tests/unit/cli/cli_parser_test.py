import mock
from nose.tools import istest

import logging
import salve
from salve.cli import parser
from tests.util import ensure_except, MockedGlobals


class TestsWithMockedIO(MockedGlobals):
    @istest
    @mock.patch('sys.argv', ['./salve.py', 'deploy', '-m', 'a/b/c'])
    def parse_cmd1(self):
        """
        Unit: Command Line Parse Deploy Manifest File Specified
        Verifies that attempting to run from the commandline successfully
        parses manifest file specification in sys.argv
        """
        p = parser.get_parser()

        args = p.parse_args()
        assert args.manifest == 'a/b/c'
        assert args.directory is None
        assert args.configfile is None

    @istest
    @mock.patch('sys.argv',
                ['./salve.py', 'deploy', '-c', 'p/q', '-m', 'root.man'])
    def parse_cmd2(self):
        """
        Unit: Command Line Parse Deploy Config File Other Order
        Verifies that attempting to run from the commandline successfully
        parses config file specification in sys.argv after the deploy
        subcommand
        """
        p = parser.get_parser()

        args = p.parse_args()
        assert args.configfile == 'p/q'
        assert args.directory is None
        assert args.manifest == 'root.man'

    @istest
    @mock.patch('sys.argv',
                ['./salve.py', '-c', 'a/b', 'deploy', '-c', 'p/q', '-m',
                 'root.man'])
    def parse_cmd3(self):
        """
        Unit: Command Line Parse Deploy Config Option Override
        Confirms that passsing an option to a subparser overrides the value it
        was given in the parent
        """
        p = parser.get_parser()

        args = p.parse_args()
        assert args.configfile == 'p/q'
        assert args.directory is None
        assert args.manifest == 'root.man'

    @istest
    @mock.patch('sys.argv', ['./salve.py', 'deploy', '-c', 'p/q'])
    def parse_cmd4(self):
        """
        Unit: Command Line Parse Deploy No Manifest
        Confirms that omitting the manifest option causes a hard abort.
        """
        p = parser.get_parser()

        ensure_except(SystemExit, p.parse_args)

    @istest
    @mock.patch('sys.argv',
                ['./salve.py', 'deploy', '-m', 'a/b/c', '-l', 'INFO'])
    def parse_cmd5(self):
        """
        Unit: Command Line Parse Set Log Level
        Checks that the log level can be set by loading args
        """
        args = parser.load_args()
        assert args.manifest == 'a/b/c'
        assert args.directory is None
        assert args.configfile is None
        assert args.log_level == 'INFO'

        assert salve.logger.level == logging.INFO
