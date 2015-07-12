from salve.class_resources import Enum, Singleton, with_metaclass

import salve.log
import salve.context

__version__ = '2.3.1'

exec_context = salve.context.ExecutionContext()

logger = salve.log.Logger(exec_context)
