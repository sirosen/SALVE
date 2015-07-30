#!/usr/bin/python

from nose.tools import istest
from tests.util import scratch

from salve.context import ExecutionContext


class TestWithScratchdir(scratch.ScratchContainer):
    @istest
    def unmet_verbosity_log_silent(self):
        """
        Unit: Log With Verbosity Too Low Is Silent
        Verifies that a logging action with the verbosity set below the min
        verbosity of the logging call is always silent.
        """
        ExecutionContext().set('verbosity', 1)
        self.logger.info('Vacuous message.', min_verbosity=2)
        assert len(self.stderr.getvalue()) == 0, self.stderr.getvalue()
