# MT5 Leveraged Trading Bot

A sophisticated trading bot for MetaTrader 5 that uses EMA, RSI, and MACD strategies with risk-managed leveraged trading to target 10-15% monthly returns.

## Features

- **MetaTrader 5 Integration**: Connects to MT5 via MetaQuotes API
- **Multi-Strategy Approach**: Uses EMA, RSI, and MACD indicators for entry/exit signals
- **Risk Management**: Leveraged trading with configurable risk parameters (1:5 leverage by default)
- **Comprehensive Logging**: Tracks all trades, P&L, and decision-making processes
- **Backtesting Framework**: Tests strategies on historical MT5 data
- **Parameter Optimization**: Uses Optuna for genetic algorithm optimization
- **24/7 Operation**: Scheduled trading with resilience and error handling
- **Multiple Currency Pairs**: Supports EURUSD, GBPUSD, USDJPY

## Installation

### Option 1: Clone from GitHub
```bash
git clone https://github.com/YOUR_USERNAME/mt5-trading-bot.git
cd mt5-trading-bot
```

### Option 2: Download ZIP
1. Download the project as ZIP from GitHub
2. Extract to your desired directory
3. Navigate to the project directory

### Setup Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configuration
1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env    # Windows
   cp .env.example .env      # macOS/Linux
   ```
2. Edit `.env` file with your MT5 credentials (see Configuration section below)

## Configuration

Update the `.env` file with your MT5 credentials:

```env
# MetaTrader 5 Configuration
MT5_ACCOUNT=YOUR_ACCOUNT_NUMBER
MT5_PASSWORD=YOUR_PASSWORD
MT5_SERVER=YOUR_BROKER_SERVER

# Trading Parameters
LEVERAGE_RATIO=5
MAX_RISK_PERCENT=2.0
TARGET_MONTHLY_RETURN=12.0

# Risk Management
MAX_OPEN_POSITIONS=3
MAX_DAILY_LOSS=5.0
MIN_BALANCE=1000
```

## Usage

### Running the Bot

```bash
python bot.py
```

### Key Components

#### 1. Strategy (`strategy.py`)
- Implements EMA, RSI, and MACD indicators
- Generates buy/sell signals based on technical analysis
- Includes parameter optimization using Optuna

#### 2. Backtesting (`backtest.py`)
- Comprehensive backtesting framework
- Performance metrics calculation
- Walk-forward analysis
- Results visualization and export

#### 3. Risk Management (`utils.py`)
- Position sizing based on account balance and risk tolerance
- Daily loss limits
- Maximum open positions control
- Leverage management

#### 4. Trading Bot (`bot.py`)
- Main execution engine
- Scheduled trading routines
- MT5 connection management
- Error handling and recovery

## Trading Strategy

The bot uses a combination of three technical indicators:

1. **EMA (Exponential Moving Average)**: Trend direction
2. **RSI (Relative Strength Index)**: Overbought/oversold conditions
3. **MACD (Moving Average Convergence Divergence)**: Momentum signals

### Entry Signals
- **Buy**: Price > EMA AND RSI < 30 AND MACD > MACD Signal
- **Sell**: Price < EMA AND RSI > 70 AND MACD < MACD Signal

## Risk Management

- **Leverage**: Configurable (default 1:5)
- **Position Size**: Calculated based on account balance and stop loss
- **Maximum Risk**: 2% of account per trade (configurable)
- **Daily Loss Limit**: 5% of account (configurable)
- **Maximum Positions**: 3 concurrent positions (configurable)

## Backtesting

Run backtests to validate strategy performance:

```python
from backtest import Backtester

backtester = Backtester(initial_balance=10000, leverage=5)
results = backtester.run_backtest(
    symbol='EURUSD',
    timeframe=60,  # 1-hour bars
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2024, 1, 1),
    strategy_params={
        'ema_period': 50,
        'rsi_period': 14,
        'macd_slow': 26,
        'macd_fast': 12,
        'macd_signal': 9
    }
)
```

## Optimization

The bot includes parameter optimization using Optuna:

```python
from strategy import optimize_parameters

# Optimize on historical data
optimized_params = optimize_parameters(df, trials=100)
```

## Logging and Monitoring

- **Trade Log**: All trades are logged to `trades.json`
- **Application Log**: Detailed logging to `trading_bot.log`
- **Performance Metrics**: Real-time P&L tracking

## Important Notes

### Prerequisites for Live Trading

1. **MetaTrader 5 Terminal**: Must be installed and running
2. **Broker Account**: Must support MT5 API access
3. **Network Connection**: Stable internet connection required
4. **Account Permissions**: Enable algorithmic trading in MT5

### Risk Warnings

⚠️ **Trading Disclaimer**: This bot involves leveraged trading which carries significant risk. You could lose more than your initial investment. 

- Always test on a demo account first
- Never risk more than you can afford to lose
- Monitor the bot regularly
- Understand the risks of automated trading

### Demo Mode

The bot can run in simulation mode without MT5 connection for:
- Strategy development
- Parameter testing
- Learning purposes

## Files Overview

- `bot.py`: Main trading bot execution
- `strategy.py`: Trading strategy implementations
- `backtest.py`: Backtesting and performance analysis
- `utils.py`: Utility functions and risk management
- `.env`: Configuration file (update with your credentials)
- `README.md`: This documentation

## Troubleshooting

### Common Issues

1. **MT5 Connection Failed**: 
   - Ensure MT5 terminal is running
   - Check credentials in `.env` file
   - Verify broker supports API access

2. **No Trading Signals**:
   - Check market hours
   - Verify symbol data availability
   - Review strategy parameters

3. **Permission Errors**:
   - Enable algorithmic trading in MT5
   - Check account permissions with broker

## Support

For issues or questions:
1. Check the logs (`trading_bot.log`)
2. Verify your MT5 setup and credentials
3. Test in demo mode first
4. Review the strategy parameters

## License

This project is for educational purposes. Use at your own risk.
