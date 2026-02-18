import logging
import logging.handlers
from datetime import datetime
from config import LOGGING_CONFIG

def setup_logger():
    """Setup logger for error recording to separate file"""
    logger = logging.getLogger('currency_service')
    logger.setLevel(getattr(logging, LOGGING_CONFIG['log_level']))
    
    logger.handlers.clear()
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = logging.handlers.RotatingFileHandler(
        LOGGING_CONFIG['log_file'],
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_error(logger, error_message, exception=None):
    """Log errors with additional information"""
    if exception:
        logger.error(f"{error_message}: {str(exception)}")
        logger.debug("Error details:", exc_info=True)
    else:
        logger.error(error_message)

def log_info(logger, message):
    """Log informational messages"""
    logger.info(message)

def log_warning(logger, message):
    """Log warning messages"""
    logger.warning(message)

logger = setup_logger()