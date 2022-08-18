from datetime import datetime

import logging


def get_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter(
        '%(asctime)s %(name)s - %(levelname)s - %(message)s - %(thread)d')
    date = datetime.today().strftime("%Y-%m-%d %H-%M-%S")

    filename = f"logs/{date}-{log_file}"
    handler = logging.FileHandler(filename, "a", "utf-8")
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
