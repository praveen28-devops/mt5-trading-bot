# MT5Trade

Free, open source MetaTrader 5 trading bot

![MT5Trade Logo](https://via.placeholder.com/300x100/009688/ffffff?text=MT5Trade)

## Features

- **MetaTrader 5 Integration**: Direct connection to MT5 terminal for live trading
- **Strategy Development**: Flexible strategy framework similar to Freqtrade
- **Backtesting**: Test your strategies against historical data
- **Risk Management**: Built-in risk management and position sizing
- **Web Interface**: Manage your bot via web UI
- **Telegram Integration**: Control and monitor via Telegram bot
- **Technical Indicators**: Extensive library of technical analysis tools
- **Machine Learning**: AI-powered strategy optimization
- **Multi-Timeframe**: Support for multiple timeframes and symbols

## Supported Markets

- **Forex**: Major, minor, and exotic currency pairs
- **Indices**: Stock market indices (S&P 500, NASDAQ, etc.)
- **Commodities**: Gold, Silver, Oil, etc.
- **Cryptocurrencies**: Bitcoin, Ethereum, and major altcoins (via MT5 brokers)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/mt5trade/mt5trade.git
cd mt5trade

# Install dependencies
pip install -e .

# Create user directory
mt5trade create-userdir --userdir user_data
```

### Configuration

```bash
# Create new configuration
mt5trade new-config --userdir user_data

# Edit the config file
# Configure your MT5 connection, strategy, and risk management settings
```

### Create a Strategy

```bash
# Generate a new strategy
mt5trade new-strategy --strategy MyStrategy --userdir user_data
```

### Run Backtest

```bash
# Download historical data
mt5trade download-data --pairs EURUSD GBPUSD --timeframes 1h 4h

# Run backtest
mt5trade backtesting --strategy MyStrategy --userdir user_data
```

### Start Trading

```bash
# Start the trading bot
mt5trade trade --strategy MyStrategy --userdir user_data
```

## Commands

### Trading
- `mt5trade trade` - Start live trading
- `mt5trade backtesting` - Run strategy backtests
- `mt5trade hyperopt` - Optimize strategy parameters

### Data Management
- `mt5trade download-data` - Download historical market data
- `mt5trade list-data` - List available data

### Strategy Development
- `mt5trade new-strategy` - Create new strategy template
- `mt5trade list-strategies` - List available strategies

### Configuration
- `mt5trade new-config` - Create new configuration
- `mt5trade create-userdir` - Create user data directory

### Information
- `mt5trade list-exchanges` - List supported exchanges/brokers
- `mt5trade list-markets` - List available trading pairs
- `mt5trade show-trades` - Show trade history

### Web Interface
- `mt5trade webserver` - Start web UI server

## Configuration

Example configuration file:

```json
{
    "max_open_trades": 3,
    "stake_currency": "USD",
    "stake_amount": 100,
    "dry_run": false,
    "mt5": {
        "account": "YOUR_MT5_ACCOUNT",
        "password": "YOUR_PASSWORD", 
        "server": "YOUR_BROKER_SERVER"
    },
    "pairlists": [
        {
            "method": "StaticPairList",
            "pairs": ["EURUSD", "GBPUSD", "USDJPY"]
        }
    ],
    "exchange": {
        "name": "mt5",
        "pair_whitelist": ["EURUSD", "GBPUSD", "USDJPY"]
    }
}
```

## Strategy Development

Basic strategy template:

```python
from mt5trade.strategy import IStrategy
from mt5trade.strategy.types import SignalType, ExitCheckTuple
import talib.abstract as ta
import pandas as pd

class MyStrategy(IStrategy):
    
    # Strategy parameters
    minimal_roi = {"0": 0.02}
    stoploss = -0.05
    timeframe = '1h'
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # Add technical indicators
        dataframe['ema20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (dataframe['close'] > dataframe['ema20']) &
            (dataframe['rsi'] < 30),
            'enter_long'] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (dataframe['rsi'] > 70),
            'exit_long'] = 1
        return dataframe
```

## Requirements

- Python 3.9+
- MetaTrader 5 terminal installed
- MT5 broker account with API access enabled

## Installation Requirements

```bash
pip install mt5trade[all]
```

Optional dependencies:
- `mt5trade[plot]` - Plotting and visualization
- `mt5trade[hyperopt]` - Parameter optimization
- `mt5trade[freqai]` - AI/ML features

## Documentation

Full documentation is available at: https://www.mt5trade.io/docs

## Contributing

We welcome contributions! Please read our [contributing guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

Always start by running a trading bot in dry-run mode and do not engage money before you understand how it works and what profit/loss you should expect.

## Support

- 📖 [Documentation](https://www.mt5trade.io/docs)
- 💬 [Discord Community](https://discord.gg/mt5trade)
- 🐛 [Issue Tracker](https://github.com/mt5trade/mt5trade/issues)
- 📧 [Email Support](mailto:support@mt5trade.io)

## Acknowledgments

This project is inspired by and follows the architectural patterns of [Freqtrade](https://github.com/freqtrade/freqtrade), adapted for MetaTrader 5 integration.
