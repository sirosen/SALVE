#!/usr/bin/python

from salve.util.context import FileContext, ExecutionContext
from salve.util.log import Logger


dummy_file_context = FileContext('no such file')
dummy_exec_context = ExecutionContext()
dummy_exec_context.set('log_level', set())

dummy_logger = Logger(dummy_exec_context)
