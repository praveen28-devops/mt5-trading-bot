import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def start_list_exchanges(args: Dict[str, Any]) -> int:
    logger.info("Listing exchanges...")
    return 0

def start_list_markets(args: Dict[str, Any]) -> int:
    logger.info("Listing markets...")
    return 0

def start_list_strategies(args: Dict[str, Any]) -> int:
    logger.info("Listing strategies...")
    return 0

def start_list_timeframes(args: Dict[str, Any]) -> int:
    logger.info("Listing timeframes...")
    return 0

def start_show_trades(args: Dict[str, Any]) -> int:
    logger.info("Showing trades...")
    return 0
