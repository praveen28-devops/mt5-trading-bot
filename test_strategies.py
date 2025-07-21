"""
Test Different Trading Strategies
"""

import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime
from backtest import Backtester
from simple_strategy import simple_moving_average_strategy, rsi_mean_reversion_strategy, guaranteed_signal_strategy
from utils import Logger

logger = Logger("StrategyTest")

def test_simple_ma_strategy():
    """Test simple moving average strategy"""
    logger.info("=== Testing Simple Moving Average Strategy ===")
    
    backtester = Backtester(initial_balance=10000, leverage=5.0)
    
    # Override the generate_trade_signal function temporarily
    original_function = backtester.run_backtest
    
    def custom_run_backtest(symbol, timeframe, start_date, end_date, strategy_params):
        # Get historical data
        df = backtester._get_historical_data(symbol, timeframe, start_date, end_date)
        
        if df.empty:
            logger.error("No historical data available")
            return {}
        
        logger.info(f"Retrieved {len(df)} bars of data")
        
        # Generate signals using simple MA strategy
        df_with_signals = simple_moving_average_strategy(df, symbol, strategy_params, for_backtest=True)
        
        if df_with_signals is None:
            logger.error("Failed to generate signals")
            return {}
        
        # Count signals
        buy_signals = df_with_signals['buy_signal'].sum()
        sell_signals = df_with_signals['sell_signal'].sum()
        logger.info(f"Generated {buy_signals} buy signals and {sell_signals} sell signals")
        
        # Execute trades based on signals
        backtester._execute_backtest_trades(df_with_signals, symbol)
        
        # Calculate performance metrics
        results = backtester._calculate_performance_metrics()
        
        return results
    
    # Test with simple MA parameters
    results = custom_run_backtest(
        'EURUSD',
        mt5.TIMEFRAME_H1,
        datetime(2023, 1, 1),
        datetime(2023, 12, 31),
        {'short_ma': 10, 'long_ma': 20}
    )
    
    if results:
        logger.info("Simple MA Strategy Results:")
        logger.info(f"  Total Return: {results.get('total_return', 0):.2%}")
        logger.info(f"  Win Rate: {results.get('win_rate', 0):.1f}%")
        logger.info(f"  Total Trades: {results.get('total_trades', 0)}")
        logger.info(f"  Profit Factor: {results.get('profit_factor', 0):.2f}")
    else:
        logger.warning("Simple MA strategy returned no results")

def test_rsi_strategy():
    """Test RSI mean reversion strategy"""
    logger.info("=== Testing RSI Mean Reversion Strategy ===")
    
    backtester = Backtester(initial_balance=10000, leverage=5.0)
    
    def custom_run_backtest(symbol, timeframe, start_date, end_date, strategy_params):
        df = backtester._get_historical_data(symbol, timeframe, start_date, end_date)
        
        if df.empty:
            logger.error("No historical data available")
            return {}
        
        logger.info(f"Retrieved {len(df)} bars of data")
        
        # Generate signals using RSI strategy
        df_with_signals = rsi_mean_reversion_strategy(df, symbol, strategy_params, for_backtest=True)
        
        if df_with_signals is None:
            logger.error("Failed to generate signals")
            return {}
        
        # Count signals
        buy_signals = df_with_signals['buy_signal'].sum()
        sell_signals = df_with_signals['sell_signal'].sum()
        logger.info(f"Generated {buy_signals} buy signals and {sell_signals} sell signals")
        
        # Execute trades
        backtester._execute_backtest_trades(df_with_signals, symbol)
        
        return backtester._calculate_performance_metrics()
    
    # Test with RSI parameters
    results = custom_run_backtest(
        'EURUSD',
        mt5.TIMEFRAME_H1,
        datetime(2023, 1, 1),
        datetime(2023, 12, 31),
        {'rsi_period': 14, 'rsi_buy_threshold': 40, 'rsi_sell_threshold': 60}
    )
    
    if results:
        logger.info("RSI Strategy Results:")
        logger.info(f"  Total Return: {results.get('total_return', 0):.2%}")
        logger.info(f"  Win Rate: {results.get('win_rate', 0):.1f}%")
        logger.info(f"  Total Trades: {results.get('total_trades', 0)}")
        logger.info(f"  Profit Factor: {results.get('profit_factor', 0):.2f}")
    else:
        logger.warning("RSI strategy returned no results")

def test_guaranteed_strategy():
    """Test guaranteed signal strategy (for system testing)"""
    logger.info("=== Testing Guaranteed Signal Strategy ===")
    
    backtester = Backtester(initial_balance=10000, leverage=5.0)
    
    def custom_run_backtest(symbol, timeframe, start_date, end_date, strategy_params):
        df = backtester._get_historical_data(symbol, timeframe, start_date, end_date)
        
        if df.empty:
            logger.error("No historical data available")
            return {}
        
        logger.info(f"Retrieved {len(df)} bars of data")
        
        # Generate signals using guaranteed strategy
        df_with_signals = guaranteed_signal_strategy(df, symbol, strategy_params, for_backtest=True)
        
        if df_with_signals is None:
            logger.error("Failed to generate signals")
            return {}
        
        # Count signals
        buy_signals = df_with_signals['buy_signal'].sum()
        sell_signals = df_with_signals['sell_signal'].sum()
        logger.info(f"Generated {buy_signals} buy signals and {sell_signals} sell signals")
        
        # Execute trades
        backtester._execute_backtest_trades(df_with_signals, symbol)
        
        return backtester._calculate_performance_metrics()
    
    # Test with guaranteed signal parameters
    results = custom_run_backtest(
        'EURUSD',
        mt5.TIMEFRAME_H1,
        datetime(2023, 1, 1),
        datetime(2023, 12, 31),
        {'signal_frequency': 50}  # Signal every 50 bars
    )
    
    if results:
        logger.info("Guaranteed Strategy Results:")
        logger.info(f"  Total Return: {results.get('total_return', 0):.2%}")
        logger.info(f"  Win Rate: {results.get('win_rate', 0):.1f}%")
        logger.info(f"  Total Trades: {results.get('total_trades', 0)}")
        logger.info(f"  Profit Factor: {results.get('profit_factor', 0):.2f}")
    else:
        logger.warning("Guaranteed strategy returned no results")

def main():
    """Run all strategy tests"""
    logger.info("Starting comprehensive strategy testing...")
    
    # Initialize MT5
    if not mt5.initialize():
        logger.error("Failed to initialize MT5")
        return
    
    try:
        # Test different strategies
        test_simple_ma_strategy()
        logger.info("")
        test_rsi_strategy()
        logger.info("")
        test_guaranteed_strategy()
        
    except Exception as e:
        logger.error(f"Error during testing: {e}")
    finally:
        mt5.shutdown()
        logger.info("Testing complete")

if __name__ == "__main__":
    main()
