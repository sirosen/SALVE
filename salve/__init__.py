import salve.util.log
import salve.util.context

exec_context = salve.util.context.ExecutionContext(
        startphase=salve.util.context.ExecutionContext.phases.STARTUP)

logger = salve.util.log.Logger(exec_context)
