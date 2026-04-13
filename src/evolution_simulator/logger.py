from config import LOGGER_LEVEL

class logger:
    def __init__(self):
        self.logger_level = LOGGER_LEVEL

    def set_logger_level(self, level):
        self.logger_level = level

    def log(self, message):
        if self.logger_level == "DEBUG":
            print(message)