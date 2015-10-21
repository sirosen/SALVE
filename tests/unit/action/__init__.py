from salve.context import FileContext
from salve.log import create_logger, NullHandler


dummy_file_context = FileContext('no such file')

dummy_logger = create_logger(__name__)
dummy_logger.handlers = [NullHandler()]
