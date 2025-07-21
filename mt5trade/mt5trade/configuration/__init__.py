"""
Configuration management for MT5Trade
"""

from mt5trade.configuration.config_validation import validate_config
from mt5trade.configuration.configuration import Configuration
from mt5trade.configuration.timerange import TimeRange


def setup_utils_configuration(args, method: str) -> dict:
    """
    Prepare the configuration for utils subcommands
    :param args: Cli args from Arguments()
    :param method: Bot running mode
    :return: Configuration
    """
    configuration = Configuration(args, method)
    config = configuration.get_config()
    
    return config


__all__ = [
    'Configuration',
    'TimeRange',
    'validate_config',
    'setup_utils_configuration'
]
