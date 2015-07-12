from salve.exceptions.base import SALVEException


class ActionException(SALVEException):
    """
    A SALVE exception specialized for Actions.
    """
    def __init__(self, msg, file_context):
        """
        ActionException constructor

        Args:
            @msg
            A string message that describes the error.
            @file_context
            A FileContext.
        """
        SALVEException.__init__(self, msg, file_context)
