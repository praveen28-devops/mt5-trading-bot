"""
Backtesting framework for MT5 Trading Bot
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import MetaTrader5 as mt5

from strategy import generate_trade_signal
from utils import MT5DataProcessor, Logger


class Backtester:
    """Backtesting engine for trading strategies"""
    
    def __init__(self, initial_balance: float = 10000, leverage: float = 5.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.leverage = leverage
        self.trades = []
        self.equity_curve = []
        self.logger = Logger("Backtester")
        
    def run_backtest(self, symbol: str, timeframe: int, start_date: datetime, 
                     end_date: datetime, strategy_params: Dict) -> Dict:
        """Run backtest on historical data"""
        
        self.logger.info(f"Starting backtest for {symbol} from {start_date} to {end_date}")
        
        # Get historical data
        df = self._get_historical_data(symbol, timeframe, start_date, end_date)
        
        if df.empty:
            self.logger.error("No historical data available")
            return {}
        
        # Generate signals
        df_with_signals = generate_trade_signal(df, **strategy_params)
        
        # Execute trades based on signals
        self._execute_backtest_trades(df_with_signals, symbol)
        
        # Calculate performance metrics
        results = self._calculate_performance_metrics()
        
        self.logger.info(f"Backtest completed. Total return: {results.get('total_return', 0):.2%}")
        
        return results
    
    def _get_historical_data(self, symbol: str, timeframe: int, 
                           start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get historical data from MT5"""
        try:
            # Calculate number of bars needed
            days_diff = (end_date - start_date).days
            bars_per_day = 24 * 60 // (timeframe // 60) if timeframe < mt5.TIMEFRAME_D1 else 1
            total_bars = days_diff * bars_per_day
            
            # Get data from MT5
            rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)
            
            if rates is None or len(rates) == 0:
                self.logger.warning(f"No data retrieved for {symbol}")
                return pd.DataFrame()
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df = MT5DataProcessor.format_symbol_data(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    def _execute_backtest_trades(self, df: pd.DataFrame, symbol: str):
        """Execute trades based on signals in backtest"""
        
        position = None  # Current position: None, 'long', or 'short'
        entry_price = 0.0
        entry_time = None
        
        for i, row in df.iterrows():
            current_price = row['close']
            
            # Close existing position if exit signal
            if position == 'long' and row['sell_signal']:
                pnl = self._calculate_pnl(entry_price, current_price, 'long', 0.1)  # 0.1 lot
                self._record_trade(symbol, 'long', entry_price, current_price, 
                                 entry_time, i, pnl, 0.1)
                self.balance += pnl
                position = None
                
            elif position == 'short' and row['buy_signal']:
                pnl = self._calculate_pnl(entry_price, current_price, 'short', 0.1)
                self._record_trade(symbol, 'short', entry_price, current_price, 
                                 entry_time, i, pnl, 0.1)
                self.balance += pnl
                position = None
            
            # Open new position if signal and no current position
            if position is None:
                if row['buy_signal']:
                    position = 'long'
                    entry_price = current_price
                    entry_time = i
                elif row['sell_signal']:
                    position = 'short'
                    entry_price = current_price
                    entry_time = i
            
            # Record equity curve
            self.equity_curve.append({
                'time': i,
                'balance': self.balance,
                'equity': self.balance  # Simplified - should include unrealized P&L
            })
    
    def _calculate_pnl(self, entry_price: float, exit_price: float, 
                      direction: str, volume: float) -> float:
        """Calculate P&L for a trade"""
        pip_value = 10  # Simplified pip value calculation
        
        if direction == 'long':
            pips = (exit_price - entry_price) * 10000  # Assuming 4-decimal currency pair
        else:  # short
            pips = (entry_price - exit_price) * 10000
        
        # Apply leverage
        pnl = pips * pip_value * volume * self.leverage
        
        return pnl
    
    def _record_trade(self, symbol: str, direction: str, entry_price: float, 
                     exit_price: float, entry_time, exit_time, pnl: float, volume: float):
        """Record a completed trade"""
        trade = {
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'entry_time': entry_time,
            'exit_time': exit_time,
            'pnl': pnl,
            'volume': volume
        }
        self.trades.append(trade)
    
    def _calculate_performance_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'total_return': 0.0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0
            }
        
        pnls = [trade['pnl'] for trade in self.trades]
        total_pnl = sum(pnls)
        total_return = total_pnl / self.initial_balance
        
        winning_trades = [pnl for pnl in pnls if pnl > 0]
        losing_trades = [pnl for pnl in pnls if pnl < 0]
        
        win_rate = len(winning_trades) / len(pnls) * 100
        
        profit_factor = (sum(winning_trades) / abs(sum(losing_trades))) if losing_trades else float('inf')
        
        # Calculate max drawdown
        max_drawdown = self._calculate_max_drawdown()
        
        # Calculate Sharpe ratio (simplified)
        if len(pnls) > 1:
            returns = np.array(pnls) / self.initial_balance
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) != 0 else 0
        else:
            sharpe_ratio = 0
        
        return {
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'total_pnl': total_pnl,
            'total_return': total_return,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'average_win': np.mean(winning_trades) if winning_trades else 0,
            'average_loss': np.mean(losing_trades) if losing_trades else 0,
            'largest_win': max(winning_trades) if winning_trades else 0,
            'largest_loss': min(losing_trades) if losing_trades else 0
        }
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if not self.equity_curve:
            return 0.0
        
        balances = [point['balance'] for point in self.equity_curve]
        peak = balances[0]
        max_dd = 0.0
        
        for balance in balances:
            if balance > peak:
                peak = balance
            drawdown = (peak - balance) / peak
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def plot_results(self):
        """Plot backtest results"""
        if not self.equity_curve:
            self.logger.warning("No equity curve data to plot")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Equity curve
        times = [point['time'] for point in self.equity_curve]
        balances = [point['balance'] for point in self.equity_curve]
        
        ax1.plot(times, balances, label='Balance', linewidth=2)
        ax1.set_title('Equity Curve')
        ax1.set_ylabel('Balance ($)')
        ax1.legend()
        ax1.grid(True)
        
        # Trade distribution
        if self.trades:
            pnls = [trade['pnl'] for trade in self.trades]
            ax2.hist(pnls, bins=30, alpha=0.7, edgecolor='black')
            ax2.set_title('P&L Distribution')
            ax2.set_xlabel('P&L ($)')
            ax2.set_ylabel('Frequency')
            ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig('backtest_results.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def export_results(self, filename: str = 'backtest_results.csv'):
        """Export backtest results to CSV"""
        if not self.trades:
            self.logger.warning("No trades to export")
            return
        
        df_trades = pd.DataFrame(self.trades)
        df_trades.to_csv(filename, index=False)
        self.logger.info(f"Results exported to {filename}")


def run_walk_forward_analysis(symbol: str, timeframe: int, total_periods: int, 
                            train_periods: int, test_periods: int) -> List[Dict]:
    """Run walk-forward analysis for strategy validation"""
    
    logger = Logger("WalkForward")
    results = []
    
    for i in range(0, total_periods - train_periods - test_periods + 1, test_periods):
        logger.info(f"Running walk-forward iteration {i // test_periods + 1}")
        
        # Define training and testing periods
        train_start = i
        train_end = i + train_periods
        test_start = train_end
        test_end = test_start + test_periods
        
        # Get training data and optimize parameters
        # This is a placeholder - implement actual optimization
        optimized_params = {
            'ema_period': 50,
            'rsi_period': 14,
            'macd_slow': 26,
            'macd_fast': 12,
            'macd_signal': 9
        }
        
        # Run backtest on test period
        backtester = Backtester()
        
        # Convert periods to actual dates (placeholder)
        start_date = datetime.now() - timedelta(days=total_periods - test_start)
        end_date = datetime.now() - timedelta(days=total_periods - test_end)
        
        test_results = backtester.run_backtest(symbol, timeframe, start_date, 
                                             end_date, optimized_params)
        
        results.append({
            'iteration': i // test_periods + 1,
            'train_start': train_start,
            'train_end': train_end,
            'test_start': test_start,
            'test_end': test_end,
            'optimized_params': optimized_params,
            'test_results': test_results
        })
    
    return results
