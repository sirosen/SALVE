import abc

from salve import with_metaclass
from salve.action.base import Action


class CreateAction(with_metaclass(abc.ABCMeta, Action)):
    """
    The base class for all CreateActions.

    Extends verification codes to include UNWRITABLE_TARGET as an error
    condition.
    """
    verification_codes = \
        Action.verification_codes.extend('UNWRITABLE_TARGET')
