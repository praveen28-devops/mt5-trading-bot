import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def start_data(args: Dict[str, Any]) -> int:
    logger.info("Starting data...")
    return 0

def start_download_data(args: Dict[str, Any]) -> int:
    logger.info("Starting download-data...")
    return 0

def start_list_data(args: Dict[str, Any]) -> int:
    logger.info("Starting list-data...")
    return 0
