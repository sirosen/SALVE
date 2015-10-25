import logging

from salve.context import ExecutionContext

# set unicode name depending on Py 2/3
try:
        unicode
except NameError:  # pragma: no cover
        unicode = str


class Formatter(logging.Formatter):
    """
    Log message formatter.
    """
    def format(self, record):
        """
        Format records according to time, current exec context, log level, and
        their message contents.

        Args:
            @record
            The LogRecord object whose attributes will be fed to the logging.
        """
        def bracket(s):
            return '[' + s + ']'
        # ensure that this custom attr exists, even if it is not defined by the
        # 'extra' kwarg
        if not hasattr(record, 'hide_salve_context'):
            record.hide_salve_context = None

        out_arr = []
        # hide_salve_context is an extra argument that may be attached to
        # LogRecords by passing the 'extra' kwarg to a log function
        if not record.hide_salve_context:
            out_arr.append(unicode(ExecutionContext()))
        out_arr.append(bracket(record.levelname))
        out_arr.append(record.msg % record.args)

        return ' '.join(out_arr)
