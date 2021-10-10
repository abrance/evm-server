
"""
操作日志记录
"""
import datetime
from loguru import logger as _logger
from pathlib import Path

project_path = Path.cwd()
log_path = Path(project_path, "log")
t = datetime.datetime.today().strftime("%Y-%m-%d_%H:%M:%S")


class Logging:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Logging, cls).__new__(cls, *args, **kwargs)

        return cls.__instance

    def __init__(self):
        self.logger = _logger
        self.setting()

    def setting(self):
        self.logger.add(sink="{}/{}.log".format(log_path, t), encoding="utf-8",
                        format="{time}-{level}-{message}", rotation="00:00", enqueue=True)

    def info(self, msg):
        return self.logger.info(msg)

    def debug(self, msg):
        return self.logger.debug(msg)

    def warning(self, msg):
        return self.logger.warning(msg)

    def error(self, msg):
        return self.logger.error(msg)


logger = Logging()


if __name__ == '__main__':
    logger.info("中文test")
    logger.debug("中文test")
    logger.warning("中文test")
    logger.error("中文test")
