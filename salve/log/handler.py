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
        # StreamHandler uses stderr if stream is None
        hdlr = logging.StreamHandler(stream=stream)

    # create a custom formatter and attach it to the handler
    hdlr.setFormatter(Formatter())
    return hdlr
