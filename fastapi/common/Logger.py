import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class Logger:
    _initialized = False

    @classmethod
    def get_logger(cls, name=__name__):
        """
        获取指定名称的 Logger（每个模块独立名称）
        """
        # 只初始化一次：将 handler 挂到 root logger，所有具名 logger 通过传播机制输出
        if not cls._initialized:
            cls._initialized = True

            BASE_DIR = Path(__file__).resolve().parent.parent # 项目根目录
            log_dir = BASE_DIR / "logs" # 日志目录
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / "app.log" # 日志文件

            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
            )

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8"
            )
            file_handler.setFormatter(formatter)

            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)
            root_logger.addHandler(console_handler)
            root_logger.addHandler(file_handler)

        return logging.getLogger(name)
