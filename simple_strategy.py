"""
Simple Trading Strategy - Guaranteed to Generate Trades
This strategy uses basic trend-following and mean-reversion concepts
"""

import pandas as pd
import numpy as np
from typing import Dict
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

def simple_moving_average_strategy(df: pd.DataFrame, symbol: str = "EURUSD", params: dict = None, for_backtest: bool = False):
    """
    Simple Moving Average Crossover Strategy
    - Buy when short MA crosses above long MA
    - Sell when short MA crosses below long MA
    """
    if df is None or df.empty:
        return None if not for_backtest else df
    
    if params is None:
        params = {
            'short_ma': 10,  # Short-term moving average
            'long_ma': 20    # Long-term moving average
        }
    
    df_copy = df.copy()
    
    try:
        # Calculate moving averages
        df_copy['ma_short'] = df_copy['close'].rolling(window=params['short_ma']).mean()
        df_copy['ma_long'] = df_copy['close'].rolling(window=params['long_ma']).mean()
        
        # Generate signals for each row (for backtesting)
        df_copy['buy_signal'] = False
        df_copy['sell_signal'] = False
        
        for i in range(1, len(df_copy)):
            if i < params['long_ma']:  # Skip rows without enough data
                continue
            
            current_short = df_copy.iloc[i]['ma_short']
            current_long = df_copy.iloc[i]['ma_long']
            prev_short = df_copy.iloc[i-1]['ma_short']
            prev_long = df_copy.iloc[i-1]['ma_long']
            
            # Buy signal: Short MA crosses above Long MA
            if prev_short <= prev_long and current_short > current_long:
                df_copy.iloc[i, df_copy.columns.get_loc('buy_signal')] = True
            
            # Sell signal: Short MA crosses below Long MA
            elif prev_short >= prev_long and current_short < current_long:
                df_copy.iloc[i, df_copy.columns.get_loc('sell_signal')] = True
        
        if for_backtest:
            return df_copy
        
        # For real-time trading, return the latest signal
        latest = df_copy.iloc[-1]
        signal = "HOLD"
        confidence = 0.6
        
        if latest['buy_signal']:
            signal = "BUY"
        elif latest['sell_signal']:
            signal = "SELL"
        
        return {
            'symbol': symbol,
            'signal': signal,
            'confidence': confidence,
            'price': latest['close'],
            'entry_price': latest['close'],
            'stop_loss': latest['close'] * 0.98 if signal == "BUY" else latest['close'] * 1.02,
            'take_profit': latest['close'] * 1.04 if signal == "BUY" else latest['close'] * 0.96,
            'ma_short': latest['ma_short'],
            'ma_long': latest['ma_long']
        }
        
    except Exception as e:
        print(f"Error in simple_moving_average_strategy: {e}")
        return None if not for_backtest else df

def rsi_mean_reversion_strategy(df: pd.DataFrame, symbol: str = "EURUSD", params: dict = None, for_backtest: bool = False):
    """
    RSI Mean Reversion Strategy
    - Buy when RSI < 40 (oversold)
    - Sell when RSI > 60 (overbought)
    """
    if df is None or df.empty:
        return None if not for_backtest else df
    
    if params is None:
        params = {
            'rsi_period': 14,
            'rsi_buy_threshold': 40,
            'rsi_sell_threshold': 60
        }
    
    df_copy = df.copy()
    
    try:
        # Calculate RSI
        rsi_indicator = RSIIndicator(df_copy['close'], window=params['rsi_period'])
        df_copy['rsi'] = rsi_indicator.rsi()
        
        # Generate signals for each row (for backtesting)
        df_copy['buy_signal'] = False
        df_copy['sell_signal'] = False
        
        for i in range(len(df_copy)):
            if i < params['rsi_period']:
                continue
            
            rsi_value = df_copy.iloc[i]['rsi']
            
            # Buy signal: RSI oversold
            if rsi_value < params['rsi_buy_threshold']:
                df_copy.iloc[i, df_copy.columns.get_loc('buy_signal')] = True
            
            # Sell signal: RSI overbought
            elif rsi_value > params['rsi_sell_threshold']:
                df_copy.iloc[i, df_copy.columns.get_loc('sell_signal')] = True
        
        if for_backtest:
            return df_copy
        
        # For real-time trading, return the latest signal
        latest = df_copy.iloc[-1]
        signal = "HOLD"
        confidence = 0.5
        
        if latest['buy_signal']:
            signal = "BUY"
            confidence = (params['rsi_buy_threshold'] - latest['rsi']) / 10
        elif latest['sell_signal']:
            signal = "SELL"  
            confidence = (latest['rsi'] - params['rsi_sell_threshold']) / 10
        
        return {
            'symbol': symbol,
            'signal': signal,
            'confidence': max(0.3, min(0.8, confidence)),
            'price': latest['close'],
            'entry_price': latest['close'],
            'stop_loss': latest['close'] * 0.995 if signal == "BUY" else latest['close'] * 1.005,
            'take_profit': latest['close'] * 1.01 if signal == "BUY" else latest['close'] * 0.99,
            'rsi': latest['rsi']
        }
        
    except Exception as e:
        print(f"Error in rsi_mean_reversion_strategy: {e}")
        return None if not for_backtest else df

def guaranteed_signal_strategy(df: pd.DataFrame, symbol: str = "EURUSD", params: dict = None, for_backtest: bool = False):
    """
    Guaranteed Signal Strategy - Generates signals every N bars for testing
    This is purely for testing the backtesting system
    """
    if df is None or df.empty:
        return None if not for_backtest else df
    
    if params is None:
        params = {
            'signal_frequency': 20  # Generate signal every 20 bars
        }
    
    df_copy = df.copy()
    
    try:
        # Generate signals for each row (for backtesting)
        df_copy['buy_signal'] = False
        df_copy['sell_signal'] = False
        
        # Alternate between buy and sell signals every N bars
        for i in range(0, len(df_copy), params['signal_frequency']):
            if i + 10 < len(df_copy):  # Ensure we don't go out of bounds
                # Alternate between buy and sell
                if (i // params['signal_frequency']) % 2 == 0:
                    df_copy.iloc[i, df_copy.columns.get_loc('buy_signal')] = True
                else:
                    df_copy.iloc[i, df_copy.columns.get_loc('sell_signal')] = True
        
        if for_backtest:
            return df_copy
        
        # For real-time trading, return the latest signal
        latest = df_copy.iloc[-1]
        signal = "BUY" if latest['buy_signal'] else ("SELL" if latest['sell_signal'] else "HOLD")
        
        return {
            'symbol': symbol,
            'signal': signal,
            'confidence': 0.7,
            'price': latest['close'],
            'entry_price': latest['close'],
            'stop_loss': latest['close'] * 0.99 if signal == "BUY" else latest['close'] * 1.01,
            'take_profit': latest['close'] * 1.02 if signal == "BUY" else latest['close'] * 0.98
        }
        
    except Exception as e:
        print(f"Error in guaranteed_signal_strategy: {e}")
        return None if not for_backtest else df
