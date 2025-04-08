import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

logger.addHandler(ch)

log_files = "app.log"
level = logging.INFO
file_handler = RotatingFileHandler(log_files, maxBytes=1000, backupCount=6)
file_handler.setLevel(level)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def get_logger():
    return logger
