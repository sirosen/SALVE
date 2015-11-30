import abc

from salve import Enum, with_metaclass
from salve.api.block import CompiledBlock
from salve.context import ExecutionContext


class Action(with_metaclass(abc.ABCMeta, CompiledBlock)):
    """
    An Action is the basis of execution.
    Actions can perform arbitrary modifications to the OS or filesystem,
    but typically are limited to moving and creating files and
    directories explicitly.
    There is no meaningful generic Action, so this is an ABC.
    """
    # by default, the only verification code is OK
    verification_codes = Enum('OK')

    def __init__(self, file_context):
        """
        Base Action constructor.

        Args:
            @file_context
            The FileContext.
        """
        self.file_context = file_context

    @property
    def prettyname(self):
        """
        Get the Pretty Name for this type of Action.
        Really, it would be desirable for this to be wrapped as both a
        classmethod and a property, but python doesn't have a built-in notion
        of a "classproperty", so just defining it as a property is fine.
        We don't really want a setter -- just a getter -- but it's okay if an
        action instance wants to be able to change its prettyname. It's just
        not clear why/how that would be useful, and it seems confusing.
        The "out of the box" functionality is just sugar for getting
        __class__.__name__, and no setter
        """
        return self.__class__.__name__

    def verify_can_exec(self, filesys):
        """
        A handler for verification codes which decides which warnings to print,
        and whether or not execution should continue.
        If it returns True, execute() will be invoked, but if it returns False,
        it will not (and None will be returned).
        May raise an exception to cause a hard abort.
        """
        code = self.get_verification_code(filesys)
        if code is self.verification_codes.OK:
            return True
        elif code not in self.verification_codes:  # pragma: no cover
            raise NotImplementedError(
                'Bad Verification Code: {0}. Should be one of {1}.'
                .format(code, self.verification_codes))
        return self.canexec_non_ok_code(code)

    def get_verification_code(self, filesys):
        """
        Verifies that the action can be executed. Returns a verification code
        from self.verification_codes.
        'OK' indicates that execution can proceed. Anything else is an error
        or warning code specific to the action type.

        Args:
            @filesys
            The filesystem, real or virtualized, against which to verify.
        """
        # transition to the action verification phase,
        # confirming execution will work
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)
        return self.verification_codes.OK

    def canexec_non_ok_code(self, code):  # pragma: no cover
        """
        Do verification on a non-OK verification code.
        Essentially acts as a generic handler for all of the common conditions
        like UNREADABLE_SOURCE or UNWRITABLE_TARGET, which may want to generate
        warnings or error messages.

        Args:
            @code
            The verification code returned by the get_verification_code check.
        """
        # for the default implementation, always silently "fail" the action and
        # skip execution
        return False

    @abc.abstractmethod
    def execute(self, filesys):  # pragma: no cover
        """
        Executes the Action.

        This is the only essential characteristic of an Action: that
        it can be executed to produce some effect.

        Args:
            @filesys
            The filesystem on which the action should be executed. Used to
            transition actions between operation on the real and virtualized
            filesystem.
        """

    def __call__(self, *args, **kwargs):
        """
        Verifies that the action can be performed, then executes it.
        """
        if self.verify_can_exec(*args, **kwargs):
            return self.execute(*args, **kwargs)
        else:
            return None
