"""
Manual Trade Execution Script
Execute immediate buy/sell orders for testing
"""

import MetaTrader5 as mt5
from datetime import datetime
import time
from utils import Logger, connect_mt5, disconnect_mt5, get_account_info
import os
from dotenv import load_dotenv

load_dotenv()

logger = Logger("ManualTrade")

# MT5 connection settings
MT5_ACCOUNT = os.getenv("MT5_ACCOUNT")
MT5_PASSWORD = os.getenv("MT5_PASSWORD") 
MT5_SERVER = os.getenv("MT5_SERVER")

def execute_market_order(symbol, order_type, volume, stop_loss=None, take_profit=None, comment="Manual Trade"):
    """Execute a market order (buy/sell)"""
    
    # Get symbol info
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        logger.error(f"Symbol {symbol} not found")
        return False
    
    if not symbol_info.visible:
        logger.info(f"Symbol {symbol} is not visible, trying to switch on")
        if not mt5.symbol_select(symbol, True):
            logger.error(f"symbol_select({symbol}) failed")
            return False
    
    # Get current tick
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        logger.error(f"Failed to get tick for {symbol}")
        return False
    
    # Determine price based on order type
    if order_type == mt5.ORDER_TYPE_BUY:
        price = tick.ask
        logger.info(f"Placing BUY order for {symbol} at {price}")
    else:
        price = tick.bid
        logger.info(f"Placing SELL order for {symbol} at {price}")
    
    # Calculate stop loss and take profit if not provided
    point = symbol_info.point
    if stop_loss is None:
        if order_type == mt5.ORDER_TYPE_BUY:
            stop_loss = price - 100 * point  # 100 points below
        else:
            stop_loss = price + 100 * point  # 100 points above
    
    if take_profit is None:
        if order_type == mt5.ORDER_TYPE_BUY:
            take_profit = price + 200 * point  # 200 points above
        else:
            take_profit = price - 200 * point  # 200 points below
    
    # Create trade request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": stop_loss,
        "tp": take_profit,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    # Send trade request
    result = mt5.order_send(request)
    
    if result is None:
        logger.error("order_send failed")
        return False
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(f"order_send failed, retcode={result.retcode}")
        return False
    
    logger.info(f"Order executed successfully:")
    logger.info(f"  Order: {result.order}")
    logger.info(f"  Volume: {result.volume}")
    logger.info(f"  Price: {result.price}")
    logger.info(f"  Comment: {result.comment}")
    
    return True

def execute_buy_order(symbol="EURUSD", volume=0.1):
    """Execute a buy order"""
    return execute_market_order(symbol, mt5.ORDER_TYPE_BUY, volume)

def execute_sell_order(symbol="EURUSD", volume=0.1):
    """Execute a sell order"""
    return execute_market_order(symbol, mt5.ORDER_TYPE_SELL, volume)

def close_all_positions(symbol=None):
    """Close all open positions for a symbol (or all symbols if None)"""
    positions = mt5.positions_get(symbol=symbol)
    
    if positions is None:
        logger.info("No positions found")
        return
    
    logger.info(f"Found {len(positions)} open positions")
    
    for position in positions:
        # Determine opposite order type to close position
        if position.type == mt5.ORDER_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(position.symbol).bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(position.symbol).ask
        
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": order_type,
            "position": position.ticket,
            "price": price,
            "comment": "Close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(close_request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"Position {position.ticket} closed successfully")
        else:
            logger.error(f"Failed to close position {position.ticket}")

def get_current_positions():
    """Get and display current positions"""
    positions = mt5.positions_get()
    
    if positions is None or len(positions) == 0:
        logger.info("No open positions")
        return
    
    logger.info(f"Current positions ({len(positions)}):")
    for position in positions:
        logger.info(f"  {position.symbol}: {position.type_str} {position.volume} @ {position.price_open}, P&L: {position.profit}")

def show_account_info():
    """Display account information"""
    account_info = get_account_info()
    if account_info:
        logger.info("Account Information:")
        logger.info(f"  Login: {account_info['login']}")
        logger.info(f"  Balance: ${account_info['balance']:.2f}")
        logger.info(f"  Equity: ${account_info['equity']:.2f}")
        logger.info(f"  Profit: ${account_info['profit']:.2f}")
        logger.info(f"  Margin: ${account_info['margin']:.2f}")
        logger.info(f"  Free Margin: ${account_info['margin_free']:.2f}")
        logger.info(f"  Leverage: 1:{account_info['leverage']}")

def interactive_trading():
    """Interactive trading menu"""
    while True:
        print("\n" + "="*50)
        print("MANUAL TRADING MENU")
        print("="*50)
        print("1. Show Account Info")
        print("2. Show Current Positions")
        print("3. Execute BUY Order (EURUSD 0.1 lot)")
        print("4. Execute SELL Order (EURUSD 0.1 lot)")
        print("5. Close All Positions")
        print("6. Custom Order")
        print("7. Exit")
        print("="*50)
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            show_account_info()
        
        elif choice == "2":
            get_current_positions()
        
        elif choice == "3":
            symbol = input("Symbol (default: EURUSD): ").strip() or "EURUSD"
            volume = input("Volume (default: 0.1): ").strip() or "0.1"
            execute_buy_order(symbol, float(volume))
        
        elif choice == "4":
            symbol = input("Symbol (default: EURUSD): ").strip() or "EURUSD"
            volume = input("Volume (default: 0.1): ").strip() or "0.1"
            execute_sell_order(symbol, float(volume))
        
        elif choice == "5":
            confirm = input("Are you sure you want to close ALL positions? (y/N): ").strip().lower()
            if confirm == 'y':
                close_all_positions()
        
        elif choice == "6":
            symbol = input("Symbol: ").strip().upper()
            order_type = input("Order type (BUY/SELL): ").strip().upper()
            volume = float(input("Volume: ").strip())
            
            if order_type == "BUY":
                execute_buy_order(symbol, volume)
            elif order_type == "SELL":
                execute_sell_order(symbol, volume)
            else:
                print("Invalid order type")
        
        elif choice == "7":
            break
        
        else:
            print("Invalid choice")

def main():
    """Main function"""
    logger.info("Manual Trading Script")
    logger.info("=" * 30)
    
    # Connect to MT5
    logger.info("Connecting to MT5...")
    if not connect_mt5(MT5_ACCOUNT, MT5_PASSWORD, MT5_SERVER):
        logger.error("Failed to connect to MT5")
        return
    
    try:
        # Show initial account info
        show_account_info()
        
        # Start interactive trading
        interactive_trading()
        
    except KeyboardInterrupt:
        logger.info("Trading interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        disconnect_mt5()
        logger.info("Disconnected from MT5")

if __name__ == "__main__":
    main()
