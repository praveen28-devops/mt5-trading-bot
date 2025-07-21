"""
Strategy Debugging and Diagnostic Tool for MT5 Trading Bot
"""

import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from strategy import generate_trade_signal, calculate_ema, calculate_rsi, calculate_macd
from utils import Logger, MT5DataProcessor

logger = Logger("StrategyDebug")

def debug_data_retrieval(symbol='EURUSD', timeframe=mt5.TIMEFRAME_H1, start_date=datetime(2023, 1, 1), end_date=datetime(2023, 12, 31)):
    """Debug data retrieval from MT5"""
    logger.info("=== DATA RETRIEVAL DEBUG ===")
    
    # Initialize MT5
    if not mt5.initialize():
        logger.error("MT5 initialization failed")
        return None
    
    # Get rates
    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)
    
    if rates is None:
        logger.error("No rates retrieved from MT5")
        return None
    
    logger.info(f"Retrieved {len(rates)} bars")
    logger.info(f"Date range: {pd.to_datetime(rates[0]['time'], unit='s')} to {pd.to_datetime(rates[-1]['time'], unit='s')}")
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    logger.info(f"OHLC Sample (first 5 rows):")
    logger.info(f"Open: {df['open'].head().values}")
    logger.info(f"High: {df['high'].head().values}")
    logger.info(f"Low: {df['low'].head().values}")
    logger.info(f"Close: {df['close'].head().values}")
    
    return df

def debug_indicators(df, params=None):
    """Debug indicator calculations"""
    logger.info("=== INDICATOR DEBUG ===")
    
    if params is None:
        params = {
            'ema_period': 50,
            'rsi_period': 14,
            'macd_slow': 26,
            'macd_fast': 12,
            'macd_signal': 9
        }
    
    # Calculate indicators
    df_copy = df.copy()
    df_copy['ema'] = calculate_ema(df_copy, params['ema_period'])
    df_copy['rsi'] = calculate_rsi(df_copy, params['rsi_period'])
    df_copy['macd'], df_copy['macd_signal'], df_copy['macd_diff'] = calculate_macd(
        df_copy, params['macd_slow'], params['macd_fast'], params['macd_signal']
    )
    
    # Sample recent values
    recent_data = df_copy.tail(10)
    logger.info(f"Recent indicator values (last 10 bars):")
    for i, row in recent_data.iterrows():
        logger.info(f"Time: {row.name}, Close: {row['close']:.5f}, EMA: {row['ema']:.5f}, RSI: {row['rsi']:.2f}, MACD: {row['macd']:.5f}")
    
    # Statistics
    logger.info(f"RSI Statistics:")
    logger.info(f"  Min: {df_copy['rsi'].min():.2f}")
    logger.info(f"  Max: {df_copy['rsi'].max():.2f}")
    logger.info(f"  Mean: {df_copy['rsi'].mean():.2f}")
    logger.info(f"  Times RSI < 30: {(df_copy['rsi'] < 30).sum()}")
    logger.info(f"  Times RSI > 70: {(df_copy['rsi'] > 70).sum()}")
    
    # Price vs EMA analysis
    price_above_ema = (df_copy['close'] > df_copy['ema']).sum()
    logger.info(f"Price above EMA: {price_above_ema} times ({price_above_ema/len(df_copy)*100:.1f}%)")
    
    return df_copy

def debug_signal_conditions(df_with_indicators, params=None):
    """Debug signal generation conditions"""
    logger.info("=== SIGNAL CONDITIONS DEBUG ===")
    
    if params is None:
        params = {
            'ema_period': 50,
            'rsi_period': 14,
            'macd_slow': 26,
            'macd_fast': 12,
            'macd_signal': 9
        }
    
    # Check individual conditions
    df = df_with_indicators.copy()
    
    # Condition checks
    price_above_ema = df['close'] > df['ema']
    price_below_ema = df['close'] < df['ema']
    rsi_oversold = df['rsi'] < 30
    rsi_overbought = df['rsi'] > 70
    macd_bullish = df['macd'] > df['macd_signal']
    macd_bearish = df['macd'] < df['macd_signal']
    
    logger.info(f"Individual condition frequencies:")
    logger.info(f"  Price > EMA: {price_above_ema.sum()} ({price_above_ema.sum()/len(df)*100:.1f}%)")
    logger.info(f"  Price < EMA: {price_below_ema.sum()} ({price_below_ema.sum()/len(df)*100:.1f}%)")
    logger.info(f"  RSI < 30: {rsi_oversold.sum()} ({rsi_oversold.sum()/len(df)*100:.1f}%)")
    logger.info(f"  RSI > 70: {rsi_overbought.sum()} ({rsi_overbought.sum()/len(df)*100:.1f}%)")
    logger.info(f"  MACD > Signal: {macd_bullish.sum()} ({macd_bullish.sum()/len(df)*100:.1f}%)")
    logger.info(f"  MACD < Signal: {macd_bearish.sum()} ({macd_bearish.sum()/len(df)*100:.1f}%)")
    
    # Combined conditions (current strategy)
    buy_conditions = price_above_ema & rsi_oversold & macd_bullish
    sell_conditions = price_below_ema & rsi_overbought & macd_bearish
    
    logger.info(f"Combined conditions (current strategy):")
    logger.info(f"  BUY signals: {buy_conditions.sum()} ({buy_conditions.sum()/len(df)*100:.3f}%)")
    logger.info(f"  SELL signals: {sell_conditions.sum()} ({sell_conditions.sum()/len(df)*100:.3f}%)")
    
    # Show actual signal dates if any
    if buy_conditions.sum() > 0:
        buy_dates = df[buy_conditions].index
        logger.info(f"BUY signal dates: {list(buy_dates)}")
    
    if sell_conditions.sum() > 0:
        sell_dates = df[sell_conditions].index
        logger.info(f"SELL signal dates: {list(sell_dates)}")

def test_relaxed_strategy(df_with_indicators):
    """Test a more relaxed strategy that should generate trades"""
    logger.info("=== TESTING RELAXED STRATEGY ===")
    
    df = df_with_indicators.copy()
    
    # More relaxed conditions
    # Buy: Price > EMA AND RSI < 40 (instead of 30)
    # Sell: Price < EMA AND RSI > 60 (instead of 70)
    
    buy_conditions = (df['close'] > df['ema']) & (df['rsi'] < 40)
    sell_conditions = (df['close'] < df['ema']) & (df['rsi'] > 60)
    
    logger.info(f"Relaxed strategy results:")
    logger.info(f"  BUY signals: {buy_conditions.sum()} ({buy_conditions.sum()/len(df)*100:.2f}%)")
    logger.info(f"  SELL signals: {sell_conditions.sum()} ({sell_conditions.sum()/len(df)*100:.2f}%)")
    
    return buy_conditions.sum() + sell_conditions.sum()

def run_full_diagnosis():
    """Run complete diagnosis"""
    logger.info("Starting full strategy diagnosis...")
    
    # Step 1: Debug data retrieval
    df = debug_data_retrieval()
    if df is None:
        logger.error("Cannot proceed without data")
        return
    
    # Step 2: Debug indicators
    df_with_indicators = debug_indicators(df)
    
    # Step 3: Debug signal conditions
    debug_signal_conditions(df_with_indicators)
    
    # Step 4: Test relaxed strategy
    total_relaxed_signals = test_relaxed_strategy(df_with_indicators)
    
    logger.info(f"=== DIAGNOSIS COMPLETE ===")
    if total_relaxed_signals == 0:
        logger.warning("Even relaxed strategy generates no signals. Check data quality.")
    else:
        logger.info(f"Relaxed strategy would generate {total_relaxed_signals} total signals")

if __name__ == "__main__":
    run_full_diagnosis()
