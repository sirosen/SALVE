from .class_resources import Enum, Singleton, with_metaclass
from .log import create_logger

__version__ = '2.4.2'

logger = create_logger(__name__)


__all__ = [
    'Enum', 'Singleton',
    'with_metaclass',
    'create_logger',

    'logger',

    '__version__'
]
