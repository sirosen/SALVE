from salve import Enum


class Token(object):
    """
    A Token is an element of an input stream that has not had any
    parsing logic applied to it.

    Tokens are mildly sensitive to their context, and may raise errors
    if found in an invalid ordering.
    """
    # these are the valid token types
    types = Enum('IDENTIFIER', 'BLOCK_START', 'BLOCK_END', 'TEMPLATE')

    def __init__(self, value, ty, file_context):
        """
        Token constructor

        Args:
            @value
            The string contained in the Token, the original element of
            the input stream.
            @ty
            The type of this token. Determined from context and content.
            @file_context
            The FileContext.
        """
        self.value = value
        self.ty = ty
        self.file_context = file_context

    def __str__(self):
        """
        stringify a Token
        """
        attrs = ['value=' + self.value, 'ty=' + self.ty,
                 'lineno=' + str(self.file_context.lineno)]
        if self.file_context.filename:
            attrs.append('filename=' + self.file_context.filename)
        return 'Token(' + ','.join(attrs) + ')'
