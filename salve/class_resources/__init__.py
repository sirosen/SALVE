# This is a package providing shared resources for the python code itself
# pertaining to class structure, heirarchy, metaclassing, &c

from .enum import Enum
from .singleton import Singleton
from .metaclass import with_metaclass


__all__ = [
    'Enum', 'Singleton',

    'with_metaclass'
]
