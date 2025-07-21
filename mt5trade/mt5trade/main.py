#!/usr/bin/env python3
"""
Main entry point for MT5Trade
"""
import logging
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any, List, Optional

from mt5trade.commands import Arguments
from mt5trade.configuration import setup_utils_configuration
from mt5trade.exceptions import ConfigurationError, MT5TradeException, OperationalException

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main(sysargv: Optional[List[str]] = None) -> None:
    """
    This function will initiate the bot and start the trading loop.
    :param sysargv: Command line arguments
    :return: None
    """

    return_code: Any = 1
    try:
        arguments = Arguments(sysargv)
        args = arguments.get_parsed_arg()

        # Call subcommand
        if 'func' in args:
            return_code = args['func'](args)
        else:
            # No subcommand was issued.
            raise OperationalException(
                "Usage of MT5Trade requires a subcommand to be specified.\n"
                "To have the bot trade with the default config, run `mt5trade trade`.\n"
                "To generate a new config file, run `mt5trade new-config`.\n"
                "To see all available subcommands, run `mt5trade --help`."
            )

    except SystemExit as e:
        return_code = e
    except KeyboardInterrupt:
        logger.info('SIGINT received, aborting ...')
        return_code = 0
    except MT5TradeException as e:
        logger.error(str(e))
        return_code = 2
    except Exception:
        logger.exception('Fatal exception!')
    finally:
        sys.exit(return_code)


if __name__ == '__main__':
    main()
