#!/usr/bin/python

import src.util.locations as locations

class StreamContext(object):
    """
    Identifies a location in the manifest tree by filename and lineno.
    """
    def __init__(self,filename,lineno):
        """
        StreamContext constructor.

        Args:
            @filename
            The file identified by the context.
            @lineno
            The line number identified by the context.
        """
        self.filename = filename
        self.lineno = lineno

    def __str__(self):
        return locations.clean_path(self.filename) + ', line ' + str(self.lineno)


class SALVEException(StandardError):
    """
    A specialized exception for errors specific to SALVE.
    """
    def __init__(self,message,context):
        """
        SALVEException constructor.

        Args:
            @message
            The string to be reported by the error.
            @context
            A StreamContext to be included in the error message.
        """
        StandardError.__init__(self,message)
        self.message = message
        self.context = context

    def to_message(self):
        """
        Convert the exception to a message string.
        """
        locstr = str(self.context)
        return 'Encountered a SALVE Exception of type ' +\
               self.__class__.__name__+ '\n'+\
               locstr + ': ' + self.message
