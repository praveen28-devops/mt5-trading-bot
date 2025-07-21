"""
Quick Test Script to Verify MT5 Trading Functionality
"""

import MetaTrader5 as mt5
from utils import connect_mt5, disconnect_mt5, get_account_info, Logger
import os
from dotenv import load_dotenv

load_dotenv()

logger = Logger("QuickTradeTest")

def test_trading_capability():
    """Test if we can execute trades"""
    
    # Connect to MT5
    MT5_ACCOUNT = os.getenv("MT5_ACCOUNT")
    MT5_PASSWORD = os.getenv("MT5_PASSWORD")
    MT5_SERVER = os.getenv("MT5_SERVER")
    
    logger.info("Testing MT5 Trading Capability...")
    
    if not connect_mt5(MT5_ACCOUNT, MT5_PASSWORD, MT5_SERVER):
        logger.error("❌ Failed to connect to MT5")
        return False
    
    logger.info("✅ Connected to MT5 successfully!")
    
    # Get account info
    account_info = get_account_info()
    logger.info(f"✅ Account: {account_info['login']}, Balance: ${account_info['balance']}")
    
    # Test symbol availability
    symbol = "EURUSD"
    symbol_info = mt5.symbol_info(symbol)
    
    if symbol_info is None:
        logger.error(f"❌ Symbol {symbol} not found")
        disconnect_mt5()
        return False
    
    logger.info(f"✅ Symbol {symbol} is available")
    
    # Check if symbol is visible
    if not symbol_info.visible:
        logger.info(f"Making {symbol} visible...")
        if not mt5.symbol_select(symbol, True):
            logger.error(f"❌ Failed to select {symbol}")
            disconnect_mt5()
            return False
        logger.info(f"✅ Symbol {symbol} is now visible")
    
    # Get current tick
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        logger.error(f"❌ Failed to get tick for {symbol}")
        disconnect_mt5()
        return False
    
    logger.info(f"✅ Current {symbol} prices: Bid={tick.bid:.5f}, Ask={tick.ask:.5f}")
    
    # Test trade request preparation (without executing)
    volume = 0.01  # Minimum lot size
    
    # Test buy order preparation
    buy_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": tick.ask,
        "sl": tick.ask - 100 * symbol_info.point,
        "tp": tick.ask + 200 * symbol_info.point,
        "comment": "Test Buy Order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    logger.info("✅ Buy order request prepared successfully")
    logger.info(f"   Symbol: {buy_request['symbol']}")
    logger.info(f"   Volume: {buy_request['volume']}")
    logger.info(f"   Price: {buy_request['price']:.5f}")
    logger.info(f"   Stop Loss: {buy_request['sl']:.5f}")
    logger.info(f"   Take Profit: {buy_request['tp']:.5f}")
    
    # Check current positions
    positions = mt5.positions_get()
    if positions is None:
        logger.info("✅ No current positions")
    else:
        logger.info(f"✅ Current positions: {len(positions)}")
        for pos in positions:
            logger.info(f"   {pos.symbol}: {pos.type_str} {pos.volume} @ {pos.price_open}, P&L: ${pos.profit:.2f}")
    
    # Check account trading permissions
    logger.info("📊 Account Trading Status:")
    logger.info(f"   Trade Allowed: {account_info.get('trade_allowed', 'Unknown')}")
    logger.info(f"   Trade Expert: {account_info.get('trade_expert', 'Unknown')}")
    
    # Test market hours
    symbol_info = mt5.symbol_info(symbol)
    logger.info(f"📈 Market Status for {symbol}:")
    logger.info(f"   Trade Mode: {symbol_info.trade_mode}")
    logger.info(f"   Full Trading: {symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL}")
    
    disconnect_mt5()
    logger.info("✅ All tests completed successfully!")
    logger.info("🎉 MT5 API is ready for trading!")
    
    return True

def execute_test_trade():
    """Execute a small test trade (optional)"""
    
    logger.info("\n" + "="*50)
    logger.info("OPTIONAL: Execute Test Trade")
    logger.info("="*50)
    
    response = input("Do you want to execute a small test trade (0.01 lot)? (y/N): ").strip().lower()
    
    if response != 'y':
        logger.info("Test trade skipped.")
        return
    
    # Connect to MT5
    MT5_ACCOUNT = os.getenv("MT5_ACCOUNT")
    MT5_PASSWORD = os.getenv("MT5_PASSWORD") 
    MT5_SERVER = os.getenv("MT5_SERVER")
    
    if not connect_mt5(MT5_ACCOUNT, MT5_PASSWORD, MT5_SERVER):
        logger.error("Failed to connect to MT5")
        return
    
    symbol = "EURUSD"
    volume = 0.01
    
    # Get current prices
    tick = mt5.symbol_info_tick(symbol)
    symbol_info = mt5.symbol_info(symbol)
    
    # Create buy order
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": tick.ask,
        "sl": tick.ask - 50 * symbol_info.point,  # 50 pip stop loss
        "tp": tick.ask + 100 * symbol_info.point,  # 100 pip take profit
        "comment": "Test Trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    logger.info(f"Executing test trade: BUY {volume} {symbol} @ {tick.ask:.5f}")
    
    result = mt5.order_send(request)
    
    if result is None:
        logger.error("❌ order_send failed - returned None")
    elif result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(f"❌ Trade failed with return code: {result.retcode}")
        logger.error(f"   Comment: {result.comment}")
    else:
        logger.info("✅ Test trade executed successfully!")
        logger.info(f"   Order: {result.order}")
        logger.info(f"   Volume: {result.volume}")
        logger.info(f"   Price: {result.price}")
        
        # Wait a moment then close the position
        import time
        time.sleep(2)
        
        # Close the position
        positions = mt5.positions_get(symbol=symbol)
        if positions and len(positions) > 0:
            pos = positions[-1]  # Get the last position
            
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": pos.volume,
                "type": mt5.ORDER_TYPE_SELL,
                "position": pos.ticket,
                "price": mt5.symbol_info_tick(symbol).bid,
                "comment": "Close test position",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            close_result = mt5.order_send(close_request)
            if close_result and close_result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info("✅ Test position closed successfully!")
            else:
                logger.warning("⚠️  Could not close test position automatically")
    
    disconnect_mt5()

if __name__ == "__main__":
    logger.info("🚀 MT5 Trading Capability Test")
    logger.info("="*40)
    
    if test_trading_capability():
        execute_test_trade()
    else:
        logger.error("❌ Trading capability test failed")
