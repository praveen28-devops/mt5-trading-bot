"""
Manual test script to demonstrate trading logic
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from utils import connect_mt5, disconnect_mt5, get_account_info, Logger
from strategy import generate_trade_signal, optimize_parameters
import os
from dotenv import load_dotenv

load_dotenv()

logger = Logger("TestTrading")

def test_live_data_and_signals():
    """Test getting live data and generating signals"""
    
    # Connect to MT5
    MT5_ACCOUNT = os.getenv("MT5_ACCOUNT")
    MT5_PASSWORD = os.getenv("MT5_PASSWORD")
    MT5_SERVER = os.getenv("MT5_SERVER")
    
    if not connect_mt5(MT5_ACCOUNT, MT5_PASSWORD, MT5_SERVER):
        logger.error("Failed to connect to MT5")
        return
    
    logger.info("Connected to MT5 successfully!")
    
    # Get account info
    account_info = get_account_info()
    logger.info(f"Account: {account_info['login']}, Balance: ${account_info['balance']}")
    
    # Test getting recent data for EURUSD
    symbol = "EURUSD"
    timeframe = mt5.TIMEFRAME_M15  # 15-minute timeframe
    
    logger.info(f"Getting recent data for {symbol}...")
    
    # Get last 200 bars
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
    
    if rates is None:
        logger.error(f"Failed to get rates for {symbol}")
        disconnect_mt5()
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    logger.info(f"Retrieved {len(df)} bars of {symbol} data")
    logger.info(f"Date range: {df['time'].min()} to {df['time'].max()}")
    logger.info(f"Latest close price: {df['close'].iloc[-1]:.5f}")
    
    # Generate trading signals
    logger.info("Generating trading signals...")
    
    # Use default parameters
    params = {
        'ema_period': 50,
        'rsi_period': 14,
        'macd_slow': 26,
        'macd_fast': 12,
        'macd_signal': 9
    }
    
    try:
        df_with_signals = generate_trade_signal(df, symbol, params, for_backtest=True)
        
        # Check recent signals
        recent_signals = df_with_signals.tail(10)
        
        logger.info("Recent market analysis:")
        for i, row in recent_signals.iterrows():
            time_str = row['time'].strftime('%Y-%m-%d %H:%M')
            close = row['close']
            rsi = row.get('rsi', 0)
            ema = row.get('ema', 0)
            buy_signal = row.get('buy_signal', False)
            sell_signal = row.get('sell_signal', False)
            
            signal_str = ""
            if buy_signal:
                signal_str = " 🟢 BUY SIGNAL"
            elif sell_signal:
                signal_str = " 🔴 SELL SIGNAL"
            
            logger.info(f"{time_str}: Close={close:.5f}, RSI={rsi:.1f}, EMA={ema:.5f}{signal_str}")
        
        # Count total signals
        buy_signals = df_with_signals['buy_signal'].sum()
        sell_signals = df_with_signals['sell_signal'].sum()
        
        logger.info(f"Total signals in last 200 bars: {buy_signals} buy, {sell_signals} sell")
        
        # Get current market info
        tick = mt5.symbol_info_tick(symbol)
        if tick:
            logger.info(f"Current market: Bid={tick.bid:.5f}, Ask={tick.ask:.5f}, Spread={tick.ask - tick.bid:.5f}")
        
    except Exception as e:
        logger.error(f"Error generating signals: {e}")
    
    disconnect_mt5()

if __name__ == "__main__":
    test_live_data_and_signals()
