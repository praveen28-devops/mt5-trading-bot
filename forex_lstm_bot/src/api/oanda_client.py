"""
OANDA API Client for Forex Trading Bot
Handles data fetching, order placement, and account management
"""

import oandapyV20
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
from loguru import logger


class OandaClient:
    """OANDA API client for forex trading operations"""
    
    def __init__(self, api_key: str, account_id: str, environment: str = "practice"):
        """
        Initialize OANDA client
        
        Args:
            api_key: OANDA API key
            account_id: OANDA account ID
            environment: 'practice' or 'live'
        """
        self.api_key = api_key
        self.account_id = account_id
        self.environment = environment
        
        # Initialize API client
        self.client = oandapyV20.API(
            access_token=api_key,
            environment=environment
        )
        
        logger.info(f"Initialized OANDA client for {environment} environment")
    
    def get_account_details(self) -> Dict:
        """Get account details and balance"""
        try:
            request = accounts.AccountDetails(accountID=self.account_id)
            response = self.client.request(request)
            return response['account']
        except Exception as e:
            logger.error(f"Error fetching account details: {e}")
            raise
    
    def get_account_balance(self) -> float:
        """Get current account balance"""
        account_info = self.get_account_details()
        return float(account_info.get('balance', 0))
    
    def get_historical_data(self, instrument: str, granularity: str = "H1", 
                          count: int = 500, from_time: str = None, 
                          to_time: str = None) -> pd.DataFrame:
        """
        Fetch historical price data
        
        Args:
            instrument: Currency pair (e.g., 'EUR_USD')
            granularity: Time frame (M1, M5, M15, M30, H1, H4, D)
            count: Number of candles to fetch
            from_time: Start time (RFC3339 format)
            to_time: End time (RFC3339 format)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            params = {
                "granularity": granularity,
                "count": count
            }
            
            if from_time:
                params["from"] = from_time
            if to_time:
                params["to"] = to_time
            
            request = instruments.InstrumentsCandles(
                instrument=instrument,
                params=params
            )
            
            response = self.client.request(request)
            candles = response['candles']
            
            # Convert to DataFrame
            data = []
            for candle in candles:
                if candle['complete']:
                    data.append({
                        'time': candle['time'],
                        'open': float(candle['mid']['o']),
                        'high': float(candle['mid']['h']),
                        'low': float(candle['mid']['l']),
                        'close': float(candle['mid']['c']),
                        'volume': int(candle['volume'])
                    })
            
            df = pd.DataFrame(data)
            df['time'] = pd.to_datetime(df['time'])
            df.set_index('time', inplace=True)
            df.sort_index(inplace=True)
            
            logger.info(f"Fetched {len(df)} candles for {instrument}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {instrument}: {e}")
            raise
    
    def get_current_prices(self, instruments: List[str]) -> Dict:
        """Get current bid/ask prices for instruments"""
        try:
            params = {"instruments": ",".join(instruments)}
            request = pricing.PricingInfo(
                accountID=self.account_id,
                params=params
            )
            
            response = self.client.request(request)
            prices = {}
            
            for price in response['prices']:
                instrument = price['instrument']
                prices[instrument] = {
                    'bid': float(price['bids'][0]['price']),
                    'ask': float(price['asks'][0]['price']),
                    'spread': float(price['asks'][0]['price']) - float(price['bids'][0]['price']),
                    'time': price['time']
                }
            
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching current prices: {e}")
            raise
    
    def place_market_order(self, instrument: str, units: int, 
                          stop_loss: float = None, take_profit: float = None) -> Dict:
        """
        Place a market order
        
        Args:
            instrument: Currency pair
            units: Position size (positive for buy, negative for sell)
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Order response
        """
        try:
            order_data = {
                "order": {
                    "type": "MARKET",
                    "instrument": instrument,
                    "units": str(units),
                    "timeInForce": "FOK"  # Fill or Kill
                }
            }
            
            # Add stop loss if specified
            if stop_loss:
                order_data["order"]["stopLossOnFill"] = {
                    "price": str(stop_loss)
                }
            
            # Add take profit if specified
            if take_profit:
                order_data["order"]["takeProfitOnFill"] = {
                    "price": str(take_profit)
                }
            
            request = orders.OrderCreate(
                accountID=self.account_id,
                data=order_data
            )
            
            response = self.client.request(request)
            
            logger.info(f"Placed market order: {units} units of {instrument}")
            return response
            
        except Exception as e:
            logger.error(f"Error placing market order: {e}")
            raise
    
    def place_limit_order(self, instrument: str, units: int, price: float,
                         stop_loss: float = None, take_profit: float = None) -> Dict:
        """
        Place a limit order
        
        Args:
            instrument: Currency pair
            units: Position size (positive for buy, negative for sell)
            price: Limit price
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Order response
        """
        try:
            order_data = {
                "order": {
                    "type": "LIMIT",
                    "instrument": instrument,
                    "units": str(units),
                    "price": str(price),
                    "timeInForce": "GTC"  # Good Till Cancelled
                }
            }
            
            # Add stop loss if specified
            if stop_loss:
                order_data["order"]["stopLossOnFill"] = {
                    "price": str(stop_loss)
                }
            
            # Add take profit if specified
            if take_profit:
                order_data["order"]["takeProfitOnFill"] = {
                    "price": str(take_profit)
                }
            
            request = orders.OrderCreate(
                accountID=self.account_id,
                data=order_data
            )
            
            response = self.client.request(request)
            
            logger.info(f"Placed limit order: {units} units of {instrument} at {price}")
            return response
            
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            raise
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        try:
            request = positions.OpenPositions(accountID=self.account_id)
            response = self.client.request(request)
            
            open_positions = []
            for position in response['positions']:
                if float(position['long']['units']) != 0 or float(position['short']['units']) != 0:
                    open_positions.append(position)
            
            return open_positions
            
        except Exception as e:
            logger.error(f"Error fetching open positions: {e}")
            raise
    
    def get_open_orders(self) -> List[Dict]:
        """Get all pending orders"""
        try:
            request = orders.OrdersPending(accountID=self.account_id)
            response = self.client.request(request)
            return response.get('orders', [])
            
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            raise
    
    def close_position(self, instrument: str, side: str = "ALL") -> Dict:
        """
        Close a position
        
        Args:
            instrument: Currency pair
            side: 'LONG', 'SHORT', or 'ALL'
            
        Returns:
            Close response
        """
        try:
            if side == "ALL":
                # Close both long and short positions
                data = {
                    "longUnits": "ALL",
                    "shortUnits": "ALL"
                }
            elif side == "LONG":
                data = {"longUnits": "ALL"}
            elif side == "SHORT":
                data = {"shortUnits": "ALL"}
            else:
                raise ValueError("Side must be 'LONG', 'SHORT', or 'ALL'")
            
            request = positions.PositionClose(
                accountID=self.account_id,
                instrument=instrument,
                data=data
            )
            
            response = self.client.request(request)
            
            logger.info(f"Closed {side} position for {instrument}")
            return response
            
        except Exception as e:
            logger.error(f"Error closing position for {instrument}: {e}")
            raise
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel a pending order"""
        try:
            request = orders.OrderCancel(
                accountID=self.account_id,
                orderID=order_id
            )
            
            response = self.client.request(request)
            
            logger.info(f"Cancelled order {order_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            raise
    
    def get_transaction_history(self, count: int = 100) -> List[Dict]:
        """Get recent transaction history"""
        try:
            import oandapyV20.endpoints.transactions as transactions
            
            request = transactions.TransactionList(
                accountID=self.account_id,
                params={"count": count}
            )
            
            response = self.client.request(request)
            return response.get('transactions', [])
            
        except Exception as e:
            logger.error(f"Error fetching transaction history: {e}")
            raise
    
    def calculate_position_size(self, instrument: str, risk_amount: float, 
                              stop_loss_pips: float) -> int:
        """
        Calculate position size based on risk management
        
        Args:
            instrument: Currency pair
            risk_amount: Amount to risk in account currency
            stop_loss_pips: Stop loss distance in pips
            
        Returns:
            Position size in units
        """
        try:
            # Get current price
            prices = self.get_current_prices([instrument])
            current_price = (prices[instrument]['bid'] + prices[instrument]['ask']) / 2
            
            # Calculate pip value (assuming account currency is USD)
            if "JPY" in instrument:
                pip_value = 0.01  # For JPY pairs, 1 pip = 0.01
            else:
                pip_value = 0.0001  # For most pairs, 1 pip = 0.0001
            
            # Calculate position size
            pip_risk = stop_loss_pips * pip_value
            position_size = int(risk_amount / (pip_risk * current_price))
            
            logger.info(f"Calculated position size: {position_size} units for {instrument}")
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0
