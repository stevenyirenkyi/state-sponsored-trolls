from cgitb import handler
import logging


def get_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter(
        '%(asctime)s %(name)s - %(levelname)s - %(message)s - %(thread)d')

    handler = logging.FileHandler("logs/"+log_file, "a", "utf-8")
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
