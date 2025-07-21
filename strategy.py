"""
Trading strategy implementations for MT5 Trading Bot
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple

from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator


def calculate_ema(df: pd.DataFrame, period: int) -> pd.Series:
    """Calculate Exponential Moving Average (EMA)"""
    ema_indicator = EMAIndicator(df['close'], window=period)
    return ema_indicator.ema_indicator()


def calculate_rsi(df: pd.DataFrame, period: int) -> pd.Series:
    """Calculate Relative Strength Index (RSI)"""
    rsi_indicator = RSIIndicator(df['close'], window=period)
    return rsi_indicator.rsi()


def calculate_macd(df: pd.DataFrame, slow: int, fast: int, signal: int) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate MACD, MACD Signal, and MACD difference"""
    macd_indicator = MACD(df['close'], window_slow=slow, window_fast=fast, window_sign=signal)
    return macd_indicator.macd(), macd_indicator.macd_signal(), macd_indicator.macd_diff()


def generate_trade_signal(df: pd.DataFrame, symbol: str = "EURUSD", params: dict = None, for_backtest: bool = False):
    """Generate trade signals based on EMA, RSI, and MACD"""
    if df is None or df.empty:
        return None if not for_backtest else df
    
    # Default parameters if not provided
    if params is None:
        params = {
            'ema_period': 50,
            'rsi_period': 14,
            'macd_slow': 26,
            'macd_fast': 12,
            'macd_signal': 9
        }
    
    df_copy = df.copy()
    
    try:
        # Calculate indicators
        df_copy['ema'] = calculate_ema(df_copy, params['ema_period'])
        df_copy['rsi'] = calculate_rsi(df_copy, params['rsi_period'])
        df_copy['macd'], df_copy['macd_signal_col'], df_copy['macd_diff'] = calculate_macd(
            df_copy, params['macd_slow'], params['macd_fast'], params['macd_signal']
        )
        
        # Generate signals for each row (for backtesting)
        df_copy['buy_signal'] = False
        df_copy['sell_signal'] = False
        
        for i in range(len(df_copy)):
            if i < max(params['ema_period'], params['rsi_period'], params['macd_slow']):
                continue  # Skip rows without enough data for indicators
                
            row = df_copy.iloc[i]
            current_price = row['close']
            ema_value = row['ema']
            rsi_value = row['rsi']
            macd_value = row['macd']
            macd_signal_value = row['macd_signal_col']
            
            # Buy signal conditions
            if (current_price > ema_value and 
                rsi_value < 30 and 
                macd_value > macd_signal_value):
                df_copy.iloc[i, df_copy.columns.get_loc('buy_signal')] = True
            
            # Sell signal conditions
            elif (current_price < ema_value and 
                  rsi_value > 70 and 
                  macd_value < macd_signal_value):
                df_copy.iloc[i, df_copy.columns.get_loc('sell_signal')] = True
        
        # If this is for backtesting, return the DataFrame with signals
        if for_backtest:
            return df_copy
        
        # For real-time trading, return the latest signal
        latest = df_copy.iloc[-1]
        current_price = latest['close']
        ema_value = latest['ema']
        rsi_value = latest['rsi']
        macd_value = latest['macd']
        macd_signal_value = latest['macd_signal_col']
        
        # Generate signal
        signal = "HOLD"
        confidence = 0.0
        
        # Buy signal conditions
        if latest['buy_signal']:
            signal = "BUY"
            confidence = min(0.8, (30 - rsi_value) / 30 + 0.3)
        
        # Sell signal conditions
        elif latest['sell_signal']:
            signal = "SELL"
            confidence = min(0.8, (rsi_value - 70) / 30 + 0.3)
        
        # Calculate stop loss and take profit
        atr = df_copy['high'].rolling(14).max() - df_copy['low'].rolling(14).min()
        atr_value = atr.iloc[-1] if not atr.empty else 0.001
        
        entry_price = current_price
        stop_loss = 0
        take_profit = 0
        
        if signal == "BUY":
            stop_loss = entry_price - (atr_value * 2)
            take_profit = entry_price + (atr_value * 3)
        elif signal == "SELL":
            stop_loss = entry_price + (atr_value * 2)
            take_profit = entry_price - (atr_value * 3)
        
        return {
            'symbol': symbol,
            'signal': signal,
            'confidence': confidence,
            'price': current_price,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'ema': ema_value,
            'rsi': rsi_value,
            'macd': macd_value,
            'macd_signal': macd_signal_value
        }
        
    except Exception as e:
        print(f"Error in generate_trade_signal: {e}")
        return None if not for_backtest else df


def optimize_parameters(df: pd.DataFrame = None, trials: int = 100) -> Dict[str, int]:
    """Optimize strategy parameters using Optuna or grid search"""
    import optuna
    from datetime import datetime, timedelta
    
    if df is None:
        # Return default parameters if no data provided
        return {
            'ema_period': 50,
            'rsi_period': 14,
            'macd_slow': 26,
            'macd_fast': 12,
            'macd_signal': 9
        }
    
    def objective(trial):
        # Define parameter ranges
        ema_period = trial.suggest_int('ema_period', 20, 100)
        rsi_period = trial.suggest_int('rsi_period', 10, 30)
        macd_slow = trial.suggest_int('macd_slow', 20, 35)
        macd_fast = trial.suggest_int('macd_fast', 8, 20)
        macd_signal = trial.suggest_int('macd_signal', 5, 15)
        
        # Generate signals with these parameters
        try:
            df_signals = generate_trade_signal(
                df, ema_period, rsi_period, macd_slow, macd_fast, macd_signal
            )
            
            # Simple backtesting to evaluate parameters
            returns = simulate_strategy_returns(df_signals)
            return returns
        except:
            return -1000  # Return poor score for invalid parameters
    
    # Create study and optimize
    study = optuna.create_study(direction='maximize', 
                               storage='sqlite:///optuna.db',
                               study_name='mt5_strategy_optimization',
                               load_if_exists=True)
    study.optimize(objective, n_trials=trials)
    
    return study.best_params


def simulate_strategy_returns(df: pd.DataFrame) -> float:
    """Simple strategy simulation for optimization"""
    if df.empty or 'buy_signal' not in df.columns or 'sell_signal' not in df.columns:
        return -1000
    
    position = 0  # 0 = no position, 1 = long, -1 = short
    returns = 0.0
    entry_price = 0.0
    
    for i, row in df.iterrows():
        current_price = row['close']
        
        if position == 0:  # No position
            if row['buy_signal']:
                position = 1
                entry_price = current_price
            elif row['sell_signal']:
                position = -1
                entry_price = current_price
        
        elif position == 1:  # Long position
            if row['sell_signal']:
                returns += (current_price - entry_price) / entry_price
                position = 0
        
        elif position == -1:  # Short position
            if row['buy_signal']:
                returns += (entry_price - current_price) / entry_price
                position = 0
    
    return returns * 100  # Return as percentage

