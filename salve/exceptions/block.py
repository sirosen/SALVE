from salve.exceptions.base import SALVEException


class BlockException(SALVEException):
    """
    A SALVE exception specialized for blocks.
    """
    def __init__(self, msg, file_context):
        """
        BlockException constructor

        Args:
            @msg
            A string message that describes the error or exception.
            @file_context
            A FileContext that identifies the origin of this
            exception.
        """
        SALVEException.__init__(self, msg, file_context=file_context)
