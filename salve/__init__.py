import salve.log
import salve.context

exec_context = salve.context.ExecutionContext(
        startphase=salve.context.ExecutionContext.phases.STARTUP)

logger = salve.log.Logger(exec_context)
