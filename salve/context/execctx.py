import salve
from salve import Enum, Singleton, with_metaclass


class ExecutionContext(with_metaclass(Singleton)):
    """
    Identifies the phase of execution, and carries any global or shared data
    from phase to phase.
    """
    phases = Enum('STARTUP', 'PARSING', 'COMPILATION', 'VERIFICATION',
                  'EXECUTION')

    def __init__(self, startphase=phases.STARTUP):
        self.phase = startphase
        self.vars = {}

    def __str__(self):
        return self.phase

    def __setitem__(self, key, value):
        self.vars[key] = value

    def __getitem__(self, key):
        return self.vars[key]

    def __contains__(self, key):
        return key in self.vars

    def transition(self, newphase, quiet=False):
        assert newphase in self.phases

        if self.phase == newphase:
            return

        if not quiet:
            transition_text = ('SALVE Execution Phase Transition ' +
                               '[%s] -> [%s]' %
                               (self.phase, newphase))
            extra = {'hide_salve_context': True}
            salve.logger.debug(transition_text, extra=extra)

        self.phase = newphase
