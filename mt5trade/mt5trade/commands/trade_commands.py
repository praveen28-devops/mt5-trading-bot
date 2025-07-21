"""
Trading command for MT5Trade
"""
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def start_trading(args: Dict[str, Any]) -> int:
    """
    Main entry point for trading mode
    :param args: Cli arguments
    :return: Return code
    """
    from mt5trade.worker import Worker
    from mt5trade.configuration import Configuration
    
    # Initialize configuration
    config = Configuration(args, "trade").get_config()
    
    # Create and start worker
    worker = Worker(config)
    
    try:
        worker.run()
    except KeyboardInterrupt:
        logger.info('SIGINT received, aborting ...')
        return 0
    except Exception as e:
        logger.error(f'Fatal exception: {e}')
        return 2
    
    return 0
