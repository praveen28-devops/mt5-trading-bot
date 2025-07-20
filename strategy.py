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


def generate_trade_signal(df: pd.DataFrame, ema_period: int = 50, rsi_period: int = 14, 
                          macd_slow: int = 26, macd_fast: int = 12, macd_signal: int = 9) -> pd.DataFrame:
    """Generate trade signals based on EMA, RSI, and MACD"""
    df = df.copy()
    
    # Calculate indicators
    df['ema'] = calculate_ema(df, ema_period)
    df['rsi'] = calculate_rsi(df, rsi_period)
    df['macd'], df['macd_signal'], df['macd_diff'] = calculate_macd(df, macd_slow, macd_fast, macd_signal)

    # Generate signals
    df['buy_signal'] = (df['close'] > df['ema']) & (df['rsi'] < 30) & (df['macd'] > df['macd_signal'])
    df['sell_signal'] = (df['close'] < df['ema']) & (df['rsi'] > 70) & (df['macd'] < df['macd_signal'])

    return df


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

