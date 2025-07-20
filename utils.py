"""
Utility functions for MT5 Trading Bot
"""

import logging
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import MetaTrader5 as mt5


class Logger:
    """Custom logger for trading bot"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Create console handler
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            # Create file handler
            file_handler = logging.FileHandler('trading_bot.log')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def debug(self, message: str):
        self.logger.debug(message)


class RiskManager:
    """Risk management utilities"""
    
    def __init__(self, max_risk_percent: float, leverage: float, max_positions: int):
        self.max_risk_percent = max_risk_percent
        self.leverage = leverage
        self.max_positions = max_positions
        self.daily_loss = 0.0
        self.open_positions = 0
        
    def calculate_position_size(self, balance: float, stop_loss_pips: float, 
                              pip_value: float) -> float:
        """Calculate position size based on risk management"""
        risk_amount = balance * (self.max_risk_percent / 100)
        position_size = risk_amount / (stop_loss_pips * pip_value)
        
        # Apply leverage
        leveraged_size = position_size * self.leverage
        
        return min(leveraged_size, balance * 0.1)  # Never risk more than 10% of balance
    
    def can_open_position(self, daily_loss_limit: float) -> bool:
        """Check if we can open a new position"""
        return (self.open_positions < self.max_positions and 
                self.daily_loss < daily_loss_limit)
    
    def update_position_count(self, change: int):
        """Update open position count"""
        self.open_positions = max(0, self.open_positions + change)
    
    def add_daily_loss(self, loss: float):
        """Add to daily loss tracking"""
        if loss < 0:
            self.daily_loss += abs(loss)
    
    def reset_daily_loss(self):
        """Reset daily loss counter"""
        self.daily_loss = 0.0


class MT5DataProcessor:
    """Data processing utilities for MT5 data"""
    
    @staticmethod
    def get_rates(symbol: str, timeframe: int, count: int) -> pd.DataFrame:
        """Get historical rates from MT5"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None:
            raise ValueError(f"Failed to get rates for {symbol}")
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    
    @staticmethod
    def calculate_pip_value(symbol: str, lot_size: float = 1.0) -> float:
        """Calculate pip value for a symbol"""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return 1.0
        
        # For most currency pairs, pip value calculation
        if symbol.endswith('USD'):
            return lot_size * 10
        else:
            # Simplified calculation - should be improved for production
            return lot_size * 10
    
    @staticmethod
    def format_symbol_data(df: pd.DataFrame) -> pd.DataFrame:
        """Format and clean symbol data"""
        df = df.copy()
        df.set_index('time', inplace=True)
        df.sort_index(inplace=True)
        
        # Remove any duplicates
        df = df[~df.index.duplicated(keep='first')]
        
        return df


class TradeLogger:
    """Logger specifically for trading activities"""
    
    def __init__(self, filename: str = "trades.json"):
        self.filename = filename
        self.trades = []
        
    def log_trade(self, trade_data: Dict):
        """Log a trade with timestamp"""
        trade_data['timestamp'] = datetime.now().isoformat()
        self.trades.append(trade_data)
        
        # Also save to file
        with open(self.filename, 'w') as f:
            json.dump(self.trades, f, indent=2)
    
    def get_daily_pnl(self, date: Optional[datetime] = None) -> float:
        """Get PnL for a specific date"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime('%Y-%m-%d')
        daily_pnl = 0.0
        
        for trade in self.trades:
            trade_date = trade['timestamp'][:10]
            if trade_date == date_str and 'pnl' in trade:
                daily_pnl += trade['pnl']
        
        return daily_pnl
    
    def get_monthly_pnl(self, year: int, month: int) -> float:
        """Get PnL for a specific month"""
        monthly_pnl = 0.0
        
        for trade in self.trades:
            trade_date = datetime.fromisoformat(trade['timestamp'].replace('Z', '+00:00'))
            if trade_date.year == year and trade_date.month == month and 'pnl' in trade:
                monthly_pnl += trade['pnl']
        
        return monthly_pnl
    
    def get_trade_stats(self) -> Dict:
        """Get comprehensive trade statistics"""
        if not self.trades:
            return {}
        
        completed_trades = [t for t in self.trades if 'pnl' in t]
        
        if not completed_trades:
            return {"total_trades": len(self.trades), "completed_trades": 0}
        
        pnls = [t['pnl'] for t in completed_trades]
        
        return {
            "total_trades": len(self.trades),
            "completed_trades": len(completed_trades),
            "total_pnl": sum(pnls),
            "average_pnl": np.mean(pnls),
            "win_rate": len([p for p in pnls if p > 0]) / len(pnls) * 100,
            "best_trade": max(pnls),
            "worst_trade": min(pnls),
            "profit_factor": abs(sum([p for p in pnls if p > 0])) / abs(sum([p for p in pnls if p < 0])) if any(p < 0 for p in pnls) else float('inf')
        }


def connect_mt5(account: str, password: str, server: str) -> bool:
    """Connect to MetaTrader 5"""
    if not mt5.initialize():
        return False
    
    if not mt5.login(int(account), password, server):
        mt5.shutdown()
        return False
    
    return True


def disconnect_mt5():
    """Disconnect from MetaTrader 5"""
    mt5.shutdown()


def get_account_info() -> Optional[Dict]:
    """Get account information"""
    account_info = mt5.account_info()
    if account_info is None:
        return None
    
    return {
        "login": account_info.login,
        "balance": account_info.balance,
        "equity": account_info.equity,
        "profit": account_info.profit,
        "margin": account_info.margin,
        "margin_free": account_info.margin_free,
        "leverage": account_info.leverage
    }


def is_market_open(symbol: str) -> bool:
    """Check if market is open for trading"""
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return False
    
    return symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL


def calculate_required_margin(symbol: str, volume: float) -> float:
    """Calculate required margin for a position"""
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return 0.0
    
    tick_info = mt5.symbol_info_tick(symbol)
    if tick_info is None:
        return 0.0
    
    # Simplified margin calculation
    return volume * tick_info.ask * symbol_info.trade_contract_size / 100000  # Assuming 1:100 base leverage
