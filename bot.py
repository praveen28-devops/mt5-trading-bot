"""
MT5 Trading Bot Main Script
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import schedule
import time
import MetaTrader5 as mt5
from typing import Dict, Optional

from utils import (
    connect_mt5, disconnect_mt5, get_account_info, Logger, TradeLogger, 
    RiskManager, MT5DataProcessor, is_market_open
)
from strategy import generate_trade_signal, optimize_parameters
from backtest import Backtester

from dotenv import load_dotenv

load_dotenv()

logger = Logger("Main")
trade_logger = TradeLogger()

# Load environment variables
MT5_ACCOUNT = os.getenv("MT5_ACCOUNT")
MT5_PASSWORD = os.getenv("MT5_PASSWORD")
MT5_SERVER = os.getenv("MT5_SERVER")
LEVERAGE_RATIO = float(os.getenv("LEVERAGE_RATIO", 5))
MAX_RISK_PERCENT = float(os.getenv("MAX_RISK_PERCENT", 2.0))
MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", 3))
MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", 5.0))
MIN_BALANCE = float(os.getenv("MIN_BALANCE", 1000))

# Trading symbols
TRADING_SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY']

# Global variables
risk_manager = None
optimized_params = None


def check_mt5_credentials():
    """Check if MT5 credentials are configured"""
    if not MT5_ACCOUNT or MT5_ACCOUNT == "YOUR_ACCOUNT_NUMBER":
        logger.error("MT5_ACCOUNT not configured. Please update .env file")
        return False
    if not MT5_PASSWORD or MT5_PASSWORD == "YOUR_PASSWORD":
        logger.error("MT5_PASSWORD not configured. Please update .env file")
        return False
    if not MT5_SERVER or MT5_SERVER == "YOUR_BROKER_SERVER":
        logger.error("MT5_SERVER not configured. Please update .env file")
        return False
    return True


def initialize_bot():
    """Initialize the trading bot"""
    global risk_manager, optimized_params
    
    logger.info("Initializing MT5 Trading Bot...")
    
    # Check credentials first
    credentials_configured = check_mt5_credentials()
    if not credentials_configured:
        logger.info("Running in simulation mode without MT5 connection")
    
    # Try to connect to MT5 (this will likely fail in demo mode)
    logger.info("Attempting to connect to MT5...")
    if not connect_mt5(MT5_ACCOUNT, MT5_PASSWORD, MT5_SERVER):
        logger.warning("Failed to connect to MT5. Running in simulation mode.")
        logger.info("To connect to actual MT5, ensure:")
        logger.info("1. MetaTrader 5 terminal is installed and running")
        logger.info("2. Your account credentials are correct in .env file")
        logger.info("3. Your broker supports MT5 API access")
        
        # Initialize with demo account info for simulation
        demo_balance = 10000.0
        logger.info(f"Using demo balance: ${demo_balance}")
        
        # Initialize risk manager
        risk_manager = RiskManager(
            max_risk_percent=MAX_RISK_PERCENT,
            leverage=LEVERAGE_RATIO,
            max_positions=MAX_OPEN_POSITIONS
        )
        
        # Use default optimized parameters
        optimized_params = optimize_parameters()
        
        return True
    
    # If connected successfully
    account_info = get_account_info()
    if account_info is None:
        logger.error("Failed to fetch account info")
        disconnect_mt5()
        return False
    
    logger.info(f"Connected to MT5 - Account: {account_info['login']}, Balance: ${account_info['balance']}")
    
    # Initialize risk manager
    risk_manager = RiskManager(
        max_risk_percent=MAX_RISK_PERCENT,
        leverage=LEVERAGE_RATIO,
        max_positions=MAX_OPEN_POSITIONS
    )
    
    # Optimize parameters with historical data
    optimized_params = optimize_parameters()
    
    return True


def run_demo_backtest():
    """Run a demonstration backtest"""
    logger.info("Running demonstration backtest...")
    
    try:
        # Create sample data for backtesting (since we might not have MT5 connection)
        backtester = Backtester(initial_balance=10000, leverage=LEVERAGE_RATIO)
        
        # Try to run backtest - this might fail without MT5 connection
        backtest_results = backtester.run_backtest(
            symbol='EURUSD',
            timeframe=mt5.TIMEFRAME_H1,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 12, 31),
            strategy_params=optimized_params
        )
        
        if backtest_results:
            logger.info(f"Backtest Results:")
            logger.info(f"  Total Return: {backtest_results.get('total_return', 0):.2%}")
            logger.info(f"  Win Rate: {backtest_results.get('win_rate', 0):.1f}%")
            logger.info(f"  Total Trades: {backtest_results.get('total_trades', 0)}")
            logger.info(f"  Profit Factor: {backtest_results.get('profit_factor', 0):.2f}")
        else:
            logger.warning("Backtest returned no results (likely due to no MT5 connection)")
            
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        logger.info("This is normal if MT5 is not connected")


def trade_routine():
    """Execute the main trading routine"""
    logger.info("Executing trade routine...")
    
    try:
        # Check if markets are open (simplified check)
        current_time = datetime.now()
        hour = current_time.hour
        
        # Skip trading during typical market closure hours (simplified)
        if hour < 6 or hour > 22:  # Assuming UTC, adjust for your timezone
            logger.info("Markets likely closed, skipping trade routine")
            return
        
        # Log current status
        if risk_manager:
            logger.info(f"Risk Status - Open positions: {risk_manager.open_positions}, Daily loss: ${risk_manager.daily_loss:.2f}")
        
        # In a real implementation, here you would:
        # 1. Get latest market data for each symbol
        # 2. Generate trading signals
        # 3. Execute trades based on signals and risk management
        # 4. Update position tracking
        
        for symbol in TRADING_SYMBOLS:
            logger.debug(f"Analyzing {symbol}...")
            
            # Check if we can open more positions
            if risk_manager and not risk_manager.can_open_position(MAX_DAILY_LOSS):
                logger.warning("Risk limits reached, skipping new trades")
                break
            
            # In simulation mode, just log what we would do
            if not mt5.initialize():
                logger.debug(f"[SIMULATION] Would analyze {symbol} for trading opportunities")
            
        logger.info("Trade routine completed")
        
    except Exception as e:
        logger.error(f"Error in trade routine: {e}")


def reset_daily_counters():
    """Reset daily risk counters"""
    if risk_manager:
        risk_manager.reset_daily_loss()
        logger.info("Daily risk counters reset")


def main():
    """Main function"""
    logger.info("="*50)
    logger.info("Starting MT5 Leveraged Trading Bot")
    logger.info(f"Target Monthly Return: {os.getenv('TARGET_MONTHLY_RETURN', 12)}%")
    logger.info(f"Leverage Ratio: 1:{LEVERAGE_RATIO}")
    logger.info(f"Max Risk per Trade: {MAX_RISK_PERCENT}%")
    logger.info("="*50)
    
    # Initialize the bot
    if not initialize_bot():
        logger.error("Failed to initialize bot")
        sys.exit(1)
    
    # Run demonstration backtest
    run_demo_backtest()
    
    # Schedule trading routines
    schedule.every().hour.at(":05").do(trade_routine)  # Run 5 minutes past each hour
    schedule.every().day.at("00:01").do(reset_daily_counters)  # Reset daily counters at midnight
    
    logger.info("Bot initialized successfully. Starting scheduled execution...")
    logger.info("Press Ctrl+C to stop the bot")
    
    # Run initial trade routine
    trade_routine()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Shutting down MT5 Trading Bot")
        if mt5.initialize():
            disconnect_mt5()
        logger.info("Bot stopped successfully")


if __name__ == "__main__":
    main()
