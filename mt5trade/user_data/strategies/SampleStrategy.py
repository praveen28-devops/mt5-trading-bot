"""
Sample Strategy for MT5Trade

This is a sample strategy to demonstrate the framework structure.
"""

import pandas as pd
from typing import Optional
import talib.abstract as ta


class SampleStrategy:
    """
    Sample trading strategy class
    """
    
    # Strategy metadata
    strategy_name = "SampleStrategy"
    minimal_roi = {
        "0": 0.02,
        "10": 0.01,
        "40": 0.005,
        "60": 0
    }
    
    stoploss = -0.05
    timeframe = '1h'
    
    # Optional: Trailing stop
    trailing_stop = False
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        Add technical indicators to the dataframe
        
        :param dataframe: OHLCV dataframe
        :param metadata: Additional information like pair name
        :return: Dataframe with indicators
        """
        
        # EMA - Exponential Moving Average
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        
        # RSI - Relative Strength Index
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        
        # Bollinger Bands
        bb = ta.BBANDS(dataframe, timeperiod=20)
        dataframe['bb_lower'] = bb['lowerband']
        dataframe['bb_middle'] = bb['middleband'] 
        dataframe['bb_upper'] = bb['upperband']
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        Populate the entry signals
        
        :param dataframe: DataFrame with indicators
        :param metadata: Additional information
        :return: DataFrame with entry signals
        """
        
        # Long entry conditions
        dataframe.loc[
            (
                (dataframe['ema_20'] > dataframe['ema_50']) &  # EMA 20 above EMA 50
                (dataframe['close'] > dataframe['ema_20']) &   # Price above EMA 20
                (dataframe['rsi'] < 70) &                      # RSI not overbought
                (dataframe['macd'] > dataframe['macdsignal'])  # MACD above signal
            ),
            'enter_long'] = 1
        
        # Short entry conditions  
        dataframe.loc[
            (
                (dataframe['ema_20'] < dataframe['ema_50']) &  # EMA 20 below EMA 50
                (dataframe['close'] < dataframe['ema_20']) &   # Price below EMA 20
                (dataframe['rsi'] > 30) &                      # RSI not oversold
                (dataframe['macd'] < dataframe['macdsignal'])  # MACD below signal
            ),
            'enter_short'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        Populate the exit signals
        
        :param dataframe: DataFrame with indicators
        :param metadata: Additional information  
        :return: DataFrame with exit signals
        """
        
        # Long exit conditions
        dataframe.loc[
            (
                (dataframe['rsi'] > 70) |                      # RSI overbought
                (dataframe['close'] < dataframe['ema_20'])     # Price below EMA 20
            ),
            'exit_long'] = 1
        
        # Short exit conditions
        dataframe.loc[
            (
                (dataframe['rsi'] < 30) |                      # RSI oversold
                (dataframe['close'] > dataframe['ema_20'])     # Price above EMA 20
            ),
            'exit_short'] = 1
        
        return dataframe
