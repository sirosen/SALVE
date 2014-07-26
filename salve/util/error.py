#!/usr/bin/python

import salve.util.locations as locations


class SALVEException(Exception):
    """
    A specialized exception for errors specific to SALVE.
    """
    def __init__(self, message, file_context):
        """
        SALVEException constructor.

        Args:
            @message
            The string to be reported by the error.
            @file_context
            A FileContext to be included in the error message.
        """
        Exception.__init__(self, message)
        self.message = message
        self.file_context = file_context
