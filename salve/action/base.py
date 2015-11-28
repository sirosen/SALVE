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
        Executes the Action.

        In a sense, this is a better description of what the "execute"
        attribute is. Calling an Action and executing it are identical.
        """
        return self.execute(*args, **kwargs)
