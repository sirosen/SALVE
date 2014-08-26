import salve.log
import salve.context

__version__ = '2.3.1'

exec_context = salve.context.ExecutionContext(
        startphase=salve.context.ExecutionContext.phases.STARTUP)

logger = salve.log.Logger(exec_context)
