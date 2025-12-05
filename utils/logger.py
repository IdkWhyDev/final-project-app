from datetime import datetime
from config.config import Config
from typing import Literal


def logger(message: str, level: Literal["INFO", "WARNING", "ERROR"]):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_text = f"[{timestamp}] [{level}] {message}\n"

    with open(Config.LOGS_PATH, "a", encoding="utf-8") as f:
        f.write(log_text)
