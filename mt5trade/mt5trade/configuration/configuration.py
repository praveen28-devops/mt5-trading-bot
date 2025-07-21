"""
Configuration management for MT5Trade
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from mt5trade.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class Configuration:
    """
    Class to read and validate configuration files
    """
    
    def __init__(self, args: Dict[str, Any], method: str = 'trade') -> None:
        self._method = method
        self._args = args
        self._config: Optional[Dict[str, Any]] = None
    
    def get_config(self) -> Dict[str, Any]:
        """
        Return the config. Will load the config if not loaded yet.
        """
        if self._config is None:
            self._config = self._load_config()
        
        return self._config
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default
        """
        config_files = self._args.get('config', [])
        
        if not config_files:
            # Look for default config files
            possible_paths = [
                Path('user_data/config.json'),
                Path('config.json'),
            ]
            
            for path in possible_paths:
                if path.exists():
                    config_files = [str(path)]
                    break
        
        if not config_files:
            logger.warning("No configuration file found, using defaults")
            return self._create_default_config()
        
        # Load configuration from file
        config_file = Path(config_files[0])
        
        if not config_file.exists():
            raise ConfigurationError(f"Configuration file '{config_file}' does not exist!")
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error reading config file: {e}")
        
        # Override config with command line arguments
        if self._args.get('strategy'):
            config['strategy'] = self._args['strategy']
        
        if self._args.get('user_data_dir'):
            config['user_data_dir'] = self._args['user_data_dir']
        
        return config
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        Create a default configuration
        """
        return {
            "max_open_trades": 3,
            "stake_currency": "USD",
            "stake_amount": 100,
            "dry_run": True,
            "strategy": "SampleStrategy",
            "user_data_dir": "user_data",
            "mt5": {
                "enabled": True
            },
            "exchange": {
                "name": "mt5",
                "pair_whitelist": ["EURUSD", "GBPUSD", "USDJPY"]
            },
            "pairlists": [
                {
                    "method": "StaticPairList"
                }
            ],
            "timeframe": "1h",
            "minimal_roi": {
                "0": 0.02,
                "10": 0.01,
                "40": 0.005,
                "60": 0
            },
            "stoploss": -0.05,
            "trailing_stop": False,
            "db_url": "sqlite:///user_data/tradesv3.sqlite"
        }
