import logging
from typing import Optional

_DEFAULT_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

_root_logger = logging.getLogger('pysystem')


def init_logger(log_file: Optional[str] = None, log_level: str = 'INFO') -> logging.Logger:
    """Initialize root logger with optional file output."""
    level = getattr(logging, str(log_level).upper(), logging.INFO)
    _root_logger.setLevel(level)
    formatter = logging.Formatter(_DEFAULT_FORMAT)
    if not _root_logger.handlers:
        stream = logging.StreamHandler()
        stream.setFormatter(formatter)
        _root_logger.addHandler(stream)
        if log_file:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(formatter)
            _root_logger.addHandler(fh)
    return _root_logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a logger using the common configuration."""
    if not _root_logger.handlers:
        init_logger()
    return _root_logger if name is None else logging.getLogger(name)
