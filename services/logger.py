import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_logging():
    # Уровень логов из env, по умолчанию INFO
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # Папка для логов
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"bot_{datetime.now():%Y%m%d}.log")

    # Формат сообщений
    fmt = "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # Корневой логгер
    root = logging.getLogger()
    root.setLevel(level)

    # Консоль
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter(fmt, datefmt))

    # Файл с ротацией (до 5 файлов по 5 МБ)
    fh = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter(fmt, datefmt))

    # Сбрасываем старые хендлеры (если есть повторный запуск)
    root.handlers = []
    root.addHandler(ch)
    root.addHandler(fh)

    # Успокоим болтливые библиотеки (при желании)
    logging.getLogger("aiogram").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)