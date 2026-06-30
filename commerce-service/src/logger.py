import logging
import sys


class Logger:
    @staticmethod
    def get_instance(name: str, level=logging.DEBUG, log_to_file=False):
        """ Set up a logger to stdout. Works for both the Docker terminal and the host machine terminal """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False

        if logger.handlers:
            return logger

        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console Handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (.log file)
        if (log_to_file):
            fileHandler = logging.FileHandler("cantelcox.log")
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)

        # Ensure root logger doesn't interfere
        logging.root.setLevel(logging.WARNING)

        return logger
