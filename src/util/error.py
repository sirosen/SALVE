#!/usr/bin/python

import src.util.locations as locations

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
            A SALVEContext to be included in the error message.
        """
        StandardError.__init__(self,message)
        self.message = message
        self.context = context
