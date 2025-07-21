"""
Command module for MT5Trade
"""
import argparse
import logging
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import command functions will be done dynamically to avoid circular imports

logger = logging.getLogger(__name__)


class Arguments:
    """
    Arguments Class. Manage the arguments received by the cli
    """

    def __init__(self, args: Optional[List[str]]) -> None:
        self.args = args
        self._parsed_arg: Optional[Dict[str, Any]] = None

    def get_parsed_arg(self) -> Dict[str, Any]:
        """
        Return the list of arguments
        :return: List[str] List of arguments
        """
        if self._parsed_arg is None:
            self._build_subcommands()
            self._parsed_arg = self._parse_args()

        return self._parsed_arg

    def _parse_args(self) -> Dict[str, Any]:
        """
        Parses given arguments and returns an argparse Namespace instance.
        """
        parsed_arg = self.parser.parse_args(self.args)
        
        # Workaround issue in argparse with action='append' and default value
        # (see https://bugs.python.org/issue16399)
        # Allow no-config for certain commands (like create-userdir) - these
        # commands must set their subparser with the no_config property
        parsed_arg = vars(parsed_arg)
        return parsed_arg

    def _build_args(self, optionlist, parser):
        """
        Builds arguments based on the given optionlist
        :param optionlist: List of Options to build
        :param parser: Parser to use
        :return: None
        """
        for val in optionlist:
            if val['short'] and val['long']:
                parser.add_argument(val['short'], val['long'], **val['kwargs'])
            elif val['short']:
                parser.add_argument(val['short'], **val['kwargs'])
            elif val['long']:
                parser.add_argument(val['long'], **val['kwargs'])

    def _build_subcommands(self) -> None:
        """
        Builds and attaches all subcommands.
        :return: None
        """
        # Build shared arguments (as group Common Options)
        _common_parser = argparse.ArgumentParser(add_help=False)
        group = _common_parser.add_argument_group("Common arguments")
        self._build_args(optionlist=AVAILABLE_CLI_OPTIONS, parser=group)

        # Build main command
        self.parser = argparse.ArgumentParser(description='Free, open source MetaTrader 5 trading bot')
        self._build_args(optionlist=AVAILABLE_CLI_OPTIONS, parser=self.parser)

        # Build sub-commands - import dynamically to avoid circular imports
        from mt5trade.commands.trade_commands import start_trading
        from mt5trade.commands.backtesting_commands import start_backtesting
        from mt5trade.commands.hyperopt_commands import start_hyperopt
        from mt5trade.commands.data_commands import (
            start_download_data, start_list_data
        )
        from mt5trade.commands.list_commands import (
            start_list_exchanges, start_list_markets, start_list_strategies,
            start_list_timeframes, start_show_trades
        )
        from mt5trade.commands.create_commands import (
            start_create_userdir, start_new_config, start_new_strategy
        )
        from mt5trade.commands.test_commands import start_test_pairlist
        from mt5trade.commands.webserver_commands import start_webserver

        subparsers = self.parser.add_subparsers(dest='command',
                                              # Use custom message when no subcommand is specified
                                              # shown from `main.py`
                                              help='MT5Trade subcommand',
                                              metavar='')

        # Add trade subcommand
        trade_cmd = subparsers.add_parser('trade', help='Trade module.',
                                        parents=[_common_parser],
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter,)
        trade_cmd.set_defaults(func=start_trading)
        self._build_args(optionlist=ARGS_TRADE, parser=trade_cmd)

        # Add backtesting subcommand  
        backtesting_cmd = subparsers.add_parser('backtesting', help='Backtesting module.',
                                              parents=[_common_parser],
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter,)
        backtesting_cmd.set_defaults(func=start_backtesting)
        self._build_args(optionlist=ARGS_BACKTEST, parser=backtesting_cmd)

        # Add hyperopt subcommand
        hyperopt_cmd = subparsers.add_parser('hyperopt', help='Hyperopt module.',
                                           parents=[_common_parser],
                                           formatter_class=argparse.ArgumentDefaultsHelpFormatter,)
        hyperopt_cmd.set_defaults(func=start_hyperopt)
        self._build_args(optionlist=ARGS_HYPEROPT, parser=hyperopt_cmd)

        # Add create-userdir subcommand
        create_userdir_cmd = subparsers.add_parser('create-userdir',
                                                  help="Create user-data directory.")
        create_userdir_cmd.set_defaults(func=start_create_userdir)
        self._build_args(optionlist=ARGS_CREATE_USERDIR, parser=create_userdir_cmd)

        # Add new-config subcommand
        build_config_cmd = subparsers.add_parser('new-config',
                                               help="Create new config")
        build_config_cmd.set_defaults(func=start_new_config)
        self._build_args(optionlist=ARGS_BUILD_CONFIG, parser=build_config_cmd)

        # Add new-strategy subcommand
        build_strategy_cmd = subparsers.add_parser('new-strategy',
                                                 help="Create new strategy")
        build_strategy_cmd.set_defaults(func=start_new_strategy)
        self._build_args(optionlist=ARGS_BUILD_STRATEGY, parser=build_strategy_cmd)

        # Add download-data subcommand
        download_data_cmd = subparsers.add_parser('download-data',
                                                help="Download backtesting data.")
        download_data_cmd.set_defaults(func=start_download_data)
        self._build_args(optionlist=ARGS_DOWNLOAD_DATA, parser=download_data_cmd)

        # Add list-data subcommand
        list_data_cmd = subparsers.add_parser('list-data',
                                            help="List downloaded data.")
        list_data_cmd.set_defaults(func=start_list_data)
        self._build_args(optionlist=ARGS_LIST_DATA, parser=list_data_cmd)

        # Add list-exchanges subcommand
        list_exchanges_cmd = subparsers.add_parser('list-exchanges',
                                                 help="Print available exchanges.")
        list_exchanges_cmd.set_defaults(func=start_list_exchanges)

        # Add list-markets subcommand
        list_markets_cmd = subparsers.add_parser('list-markets',
                                               help="Print markets on exchange.")
        list_markets_cmd.set_defaults(func=start_list_markets)
        self._build_args(optionlist=ARGS_LIST_MARKETS, parser=list_markets_cmd)

        # Add list-strategies subcommand
        list_strategies_cmd = subparsers.add_parser('list-strategies',
                                                  help="Print available strategies.")
        list_strategies_cmd.set_defaults(func=start_list_strategies)
        self._build_args(optionlist=ARGS_LIST_STRATEGIES, parser=list_strategies_cmd)

        # Add list-timeframes subcommand
        list_timeframes_cmd = subparsers.add_parser('list-timeframes',
                                                  help="Print available timeframes.")
        list_timeframes_cmd.set_defaults(func=start_list_timeframes)
        self._build_args(optionlist=ARGS_LIST_TIMEFRAMES, parser=list_timeframes_cmd)

        # Add show-trades subcommand
        show_trades_cmd = subparsers.add_parser('show-trades',
                                              help="Show trades.")
        show_trades_cmd.set_defaults(func=start_show_trades)
        self._build_args(optionlist=ARGS_SHOW_TRADES, parser=show_trades_cmd)

        # Add test-pairlist subcommand
        test_pairlist_cmd = subparsers.add_parser('test-pairlist',
                                                help="Test your pairlist configuration.")
        test_pairlist_cmd.set_defaults(func=start_test_pairlist)
        self._build_args(optionlist=ARGS_TEST_PAIRLIST, parser=test_pairlist_cmd)

        # Add webserver subcommand
        webserver_cmd = subparsers.add_parser('webserver', help='Webserver module.')
        webserver_cmd.set_defaults(func=start_webserver)
        self._build_args(optionlist=ARGS_WEBSERVER, parser=webserver_cmd)


# Common CLI options
AVAILABLE_CLI_OPTIONS = [
    # Main options
    {"short": "-V", "long": "--version",
     "kwargs": {"action": "version", "version": f"%(prog)s 2025.1"}},
    {"short": "-c", "long": "--config",
     "kwargs": {"help": f"Specify configuration file (default: `userdir/config.json` or `config.json` whichever exists). "
                        f"Multiple --config options may be used. Can be set to `-` to read config from stdin.",
                "dest": "config", "default": [], "action": "append",
                "metavar": "PATH"}},
    {"short": "-d", "long": "--datadir",
     "kwargs": {"help": "Path to directory with historical backtesting data.",
                "dest": "datadir", "default": None, "metavar": "PATH"}},
    {"short": "-s", "long": "--strategy",
     "kwargs": {"help": "Specify strategy class name which will be used by the bot.",
                "dest": "strategy", "default": None, "metavar": "NAME"}},
    {"short": "--strategy-path", "long": "",
     "kwargs": {"help": "Specify additional strategy lookup path.",
                "dest": "strategy_path", "default": None, "metavar": "PATH"}},
    {"short": "--userdir", "long": "",
     "kwargs": {"help": "Path to userdata directory.",
                "dest": "user_data_dir", "default": None, "metavar": "PATH"}},
]

# Arguments for trade subcommand
ARGS_TRADE = []

# Arguments for backtesting subcommand
ARGS_BACKTEST = []

# Arguments for hyperopt subcommand  
ARGS_HYPEROPT = []

# Other argument groups would go here...
ARGS_CREATE_USERDIR = [
    {"short": "--userdir", "long": "",
     "kwargs": {"help": "Path to create user data directory.",
                "dest": "user_data_dir", "default": "user_data", "metavar": "PATH"}},
]
ARGS_BUILD_CONFIG = []
ARGS_BUILD_STRATEGY = []
ARGS_DOWNLOAD_DATA = []
ARGS_LIST_DATA = []
ARGS_LIST_MARKETS = []
ARGS_LIST_STRATEGIES = []
ARGS_LIST_TIMEFRAMES = []
ARGS_SHOW_TRADES = []
ARGS_TEST_PAIRLIST = []
ARGS_WEBSERVER = []
