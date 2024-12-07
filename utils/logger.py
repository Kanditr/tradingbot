import logging
import os

def initialize_logging():
    """
    Set up the logging configuration.
    """
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    logging.info('Logger initialized with level: %s', log_level)