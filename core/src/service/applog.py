import logging
import os

class AppLogService:
    """
        A service dedicated for writting log.
        This log service does 2 things:
        - log warning level to the console
        - log error level to file
    """
    def __init__(self, name):
        self.env_path = os.path.dirname(__file__)
        self.path = f"{self.env_path}/../../../logs"
        self.name = name
        self.logger = self.__build_logger()
        return

    def __build_logger(self):
        logger = logging.getLogger(name=self.name)
        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(filename=f"{self.path}/{self.name}")
        c_handler.setLevel(logging.WARNING)
        f_handler.setLevel(logging.ERROR)

        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
        return logger