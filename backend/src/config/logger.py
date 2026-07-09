import logging
import os
from datetime import datetime

# =====================================================
# LOG DIRECTORY
# =====================================================

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# =====================================================
# LOG FILE
# =====================================================

LOG_FILE = os.path.join(
    LOG_DIR,
    f"{datetime.now().strftime('%Y-%m-%d')}.log"
)

# =====================================================
# LOGGER
# =====================================================

logger = logging.getLogger("AITasker")

logger.setLevel(logging.INFO)

# Tránh tạo nhiều handler khi import nhiều lần
if not logger.handlers:

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ===========================
    # FILE HANDLER
    # ===========================

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # ===========================
    # CONSOLE HANDLER
    # ===========================

    console_handler = logging.StreamHandler()

    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def info(message: str):
    logger.info(message)


def warning(message: str):
    logger.warning(message)


def error(message: str):
    logger.error(message)


def critical(message: str):
    logger.critical(message)


def debug(message: str):
    logger.debug(message)