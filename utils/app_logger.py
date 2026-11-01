import os
import logging
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure main error log file
error_log_path = os.path.join(LOG_DIR, "agent_errors.log")

logger = logging.getLogger("AiJobAgent")
logger.setLevel(logging.ERROR)

# File handler for error logging
file_handler = logging.FileHandler(error_log_path, encoding="utf-8")
file_formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
)
file_handler.setFormatter(file_formatter)

if not logger.handlers:
    logger.addHandler(file_handler)

def log_error(platform: str, context_msg: str, exception: Exception):
    """
    Logs detailed exception details and stack traces to logs/agent_errors.log.
    """
    error_msg = f"[{platform}] {context_msg} | Error: {str(exception)}"
    logger.error(error_msg, exc_info=True)
    print(f"❌ [ERROR LOGGED] {error_msg}")