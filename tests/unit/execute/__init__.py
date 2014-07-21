#!/usr/bin/python

from salve.util.context import SALVEContext, StreamContext, ExecutionContext
from salve.util.log import Logger


dummy_stream_context = StreamContext('no such file', -1)
dummy_exec_context = ExecutionContext()
dummy_context = SALVEContext(exec_context=dummy_exec_context,
        stream_context=dummy_stream_context)
dummy_exec_context.set('log_level', set())

dummy_logger = Logger(dummy_exec_context)
