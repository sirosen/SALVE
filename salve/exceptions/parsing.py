from salve.exceptions.base import SALVEException


class ParsingException(SALVEException):
    """
    A specialized exception for parsing errors.

    A ParsingException (PE) often carres the token that tripped the
    exception in its message.
    """
    def __init__(self, msg, file_context):
        """
        ParsingException constructor

        Args:
            @msg
            A string message that describes the error.
            @file_context
            The FileContext.
        """
        SALVEException.__init__(self, msg, file_context)


class TokenizationException(ParsingException):
    """
    A SALVE exception specialized for tokenization.
    """
    def __init__(self, msg, file_context):
        """
        TokenizationException constructor

        Args:
            @msg
            A string message that describes the error.
            @file_context
            The FileContext.
        """
        SALVEException.__init__(self, msg, file_context)
