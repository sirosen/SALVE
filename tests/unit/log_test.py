import logging
from nose.tools import istest

import salve.log
from tests.util import scratch, assert_substr, ensure_except


class TestWithScratchdir(scratch.ScratchContainer):
    @istest
    def clear_logging_handlers(self):
        """
        Unit: Logging Clear Handlers
        Tests that emptying logging handlers causes logging to "go dark".
        """
        msg = 'test log msg'
        expected = 'STARTUP [INFO] {0}\n'.format(msg)
        self.logger.info(msg)
        salve.log.clear_handlers(self.logger)
        self.logger.info('no show log msg')

        err = self.stderr.getvalue()

        assert_substr(err, expected)

        assert 'no show log msg' not in err, err

    @istest
    def str_to_loglevel(self):
        """
        Unit: Logging Str to Log Level
        Tests that various log levels map correctly to stdlib logging log
        levels
        """
        assert salve.log.str_to_level('DEBUG') == logging.DEBUG
        assert salve.log.str_to_level('INFO') == logging.INFO
        assert salve.log.str_to_level('WARNING') == logging.WARNING
        assert salve.log.str_to_level('ERROR') == logging.ERROR

    @istest
    def invalid_str_to_loglevel(self):
        """
        Unit: Logging Invalid Str to Log Level
        Tests that a bad log levels string produces a ValueError, when mapped
        to a logging log level.
        """
        assert salve.log.str_to_level('DEBUG') == logging.DEBUG
        assert salve.log.str_to_level('INFO') == logging.INFO
        assert salve.log.str_to_level('WARNING') == logging.WARNING
        assert salve.log.str_to_level('ERROR') == logging.ERROR
        ensure_except(ValueError, salve.log.str_to_level, 'INVALID_LOG_LEVEL')
