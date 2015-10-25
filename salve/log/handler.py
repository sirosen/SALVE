import sys
import logging

from .formatter import Formatter


def gen_handler(filename=None, stream=None):
    """
    Generate a log handler for either a file or a stream. If both are
    specified, only use the filename. If neither is specified, use stderr.

    KWArgs:
        @filename=None
        The file to which messages should be logged. If specified, takes
        precedence over @stream.

        @stream=None
        The file-like object to which log messages should be streamed.
    """
    if filename:
        hdlr = logging.FileHandler(filename)
    else:
        # setting the stream varies between 2.6 and 2.7+
        # check for 2.6 to do it the old way if that's the case
        shortver = sys.version_info[:2]
        if shortver == (2, 6):  # pragma: no cover
            # case where the stream handler is specified, pass it as the first
            # arg
            if stream:
                hdlr = logging.StreamHandler(stream)
            # case where it's unspecified, omit it so that StreamHandler
            # defaults to sys.stderr
            else:
                hdlr = logging.StreamHandler()
        else:
            # StreamHandler uses stderr if stream is None
            hdlr = logging.StreamHandler(stream=stream)

    # create a custom formatter and attach it to the handler
    hdlr.setFormatter(Formatter())
    return hdlr


try:
    NullHandler = logging.NullHandler

# on Python 2.6, there is no NullHandler, so we must define our own (which is
# quite simple to do)
except AttributeError:  # pragma: no cover
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
