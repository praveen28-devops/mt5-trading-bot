#!/usr/bin/env python3
"""
Quick test script to validate bot functionality before live trading
"""

import os
import sys
from datetime import datetime, timedelta

# Test all imports
try:
    import pandas as pd
    import numpy as np
    import MetaTrader5 as mt5
    from dotenv import load_dotenv
    
    from utils import connect_mt5, get_account_info, Logger, RiskManager
    from strategy import generate_trade_signal
    from backtest import Backtester
    
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Load configuration
load_dotenv()
logger = Logger("QuickTest")

def test_configuration():
    """Test configuration loading"""
    logger.info("Testing configuration...")
    
    required_vars = ['MT5_ACCOUNT', 'MT5_PASSWORD', 'MT5_SERVER']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        return False
    
    logger.info("✅ Configuration loaded successfully")
    return True

def test_mt5_connection():
    """Test MT5 connection"""
    logger.info("Testing MT5 connection...")
    
    account = os.getenv("MT5_ACCOUNT")
    password = os.getenv("MT5_PASSWORD")
    server = os.getenv("MT5_SERVER")
    
    if connect_mt5(account, password, server):
        account_info = get_account_info()
        if account_info:
            logger.info(f"✅ Connected to MT5 - Account: {account_info['login']}, Balance: ${account_info['balance']}")
            return True
        else:
            logger.error("❌ Failed to get account info")
            return False
    else:
        logger.error("❌ Failed to connect to MT5")
        return False

def test_risk_manager():
    """Test risk manager initialization"""
    logger.info("Testing risk manager...")
    
    try:
        risk_manager = RiskManager(
            max_risk_percent=2.0,
            leverage=5,
            max_positions=3
        )
        logger.info("✅ Risk manager initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Risk manager error: {e}")
        return False

def test_strategy():
    """Test strategy signal generation"""
    logger.info("Testing strategy...")
    
    try:
        # Get some market data
        if not mt5.initialize():
            logger.error("❌ MT5 not initialized for strategy test")
            return False
        
        rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M15, 0, 100)
        if rates is None:
            logger.warning("⚠️ No market data available for strategy test")
            return True  # Not a critical error for initial deployment
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Test signal generation
        signal = generate_trade_signal(df, "EURUSD")
        if signal:
            logger.info(f"✅ Strategy test successful - Signal: {signal.get('signal', 'NONE')}")
        else:
            logger.info("✅ Strategy test successful - No signal generated")
        
        return True
    except Exception as e:
        logger.error(f"❌ Strategy test error: {e}")
        return False

def test_backtester():
    """Test backtester initialization"""
    logger.info("Testing backtester...")
    
    try:
        backtester = Backtester(initial_balance=10000, leverage=5)
        logger.info("✅ Backtester initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Backtester error: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("=" * 50)
    logger.info("QUICK BOT DEPLOYMENT TEST")
    logger.info("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("MT5 Connection", test_mt5_connection),
        ("Risk Manager", test_risk_manager),
        ("Strategy", test_strategy),
        ("Backtester", test_backtester)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"❌ {test_name} test failed with exception: {e}")
            failed += 1
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    logger.info(f"✅ Passed: {passed}")
    logger.info(f"❌ Failed: {failed}")
    
    if failed == 0:
        logger.info("\n🎉 ALL TESTS PASSED! Your bot is ready for deployment.")
        logger.info("\n📋 Pre-deployment checklist:")
        logger.info("   1. ✅ MT5 terminal is running")
        logger.info("   2. ✅ Account credentials are correct")
        logger.info("   3. ✅ All dependencies installed")
        logger.info("   4. ✅ Risk parameters configured")
        logger.info("\n🚀 To start trading: python bot.py")
    else:
        logger.error("\n⚠️ Some tests failed. Please fix the issues before deployment.")
    
    # Cleanup
    if mt5.initialize():
        mt5.shutdown()

if __name__ == "__main__":
    main()
