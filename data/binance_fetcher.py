"""
Binance exchange data fetcher for CryptoGap+
"""
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
import time
import logging
from typing import Dict, List, Optional

from config.config import BINANCE_API_KEY, BINANCE_API_SECRET, TOP_CRYPTOS, MARKETS

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('binance_fetcher')

class BinanceFetcher:
    """Class to fetch cryptocurrency data from Binance"""
    
    def __init__(self, api_key: str = BINANCE_API_KEY, api_secret: str = BINANCE_API_SECRET):
        """Initialize the Binance client"""
        self.client = Client(api_key, api_secret) if api_key and api_secret else Client()
        logger.info("Binance fetcher initialized")
        
    def get_ticker_prices(self) -> Dict[str, float]:
        """
        Get current prices for all tickers
        
        Returns:
            Dict[str, float]: Dictionary of symbol-price pairs
        """
        try:
            all_tickers = self.client.get_all_tickers()
            return {ticker['symbol']: float(ticker['price']) for ticker in all_tickers}
        except BinanceAPIException as e:
            logger.error(f"Error fetching ticker prices: {e}")
            return {}
            
    def get_top_crypto_prices(self, cryptos: List[str] = TOP_CRYPTOS, markets: List[str] = MARKETS) -> pd.DataFrame:
        """
        Get prices for top cryptocurrencies across specified markets
        
        Args:
            cryptos (List[str]): List of crypto symbols to fetch
            markets (List[str]): List of markets to fetch prices for
            
        Returns:
            pd.DataFrame: DataFrame with crypto prices across markets
        """
        try:
            all_prices = self.get_ticker_prices()
            
            # Create empty DataFrame
            data = []
            
            # Populate data
            for crypto in cryptos:
                row = {'Symbol': crypto}
                
                for market in markets:
                    if crypto == market:
                        # Skip if crypto is the same as market (e.g., BTC/BTC)
                        continue
                        
                    symbol = f"{crypto}{market}"
                    if symbol in all_prices:
                        row[f"{market}_price"] = all_prices[symbol]
                    else:
                        # Try reverse pair if direct pair doesn't exist
                        reverse_symbol = f"{market}{crypto}"
                        if reverse_symbol in all_prices:
                            row[f"{market}_price"] = 1 / all_prices[reverse_symbol]
                        else:
                            row[f"{market}_price"] = None
                
                data.append(row)
            
            return pd.DataFrame(data)
        
        except Exception as e:
            logger.error(f"Error fetching top crypto prices: {e}")
            return pd.DataFrame()
    
    def get_24h_stats(self, symbol: str) -> Dict:
        """
        Get 24-hour statistics for a specific symbol
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Dict: Dictionary containing 24h statistics
        """
        try:
            stats = self.client.get_ticker(symbol=symbol)
            return {
                'symbol': stats['symbol'],
                'price_change': float(stats['priceChange']),
                'price_change_percent': float(stats['priceChangePercent']),
                'weighted_avg_price': float(stats['weightedAvgPrice']),
                'prev_close_price': float(stats['prevClosePrice']),
                'last_price': float(stats['lastPrice']),
                'last_qty': float(stats['lastQty']),
                'bid_price': float(stats['bidPrice']),
                'bid_qty': float(stats['bidQty']),
                'ask_price': float(stats['askPrice']),
                'ask_qty': float(stats['askQty']),
                'open_price': float(stats['openPrice']),
                'high_price': float(stats['highPrice']),
                'low_price': float(stats['lowPrice']),
                'volume': float(stats['volume']),
                'quote_volume': float(stats['quoteVolume']),
                'open_time': stats['openTime'],
                'close_time': stats['closeTime'],
                'count': stats['count']
            }
        except BinanceAPIException as e:
            logger.error(f"Error fetching 24h stats for {symbol}: {e}")
            return {}
    
    def get_detailed_coin_info(self, symbol: str, market: str = 'USDT') -> Dict:
        """
        Get detailed information for a specific coin
        
        Args:
            symbol (str): Coin symbol (e.g., 'BTC')
            market (str): Market to get info against (e.g., 'USDT')
            
        Returns:
            Dict: Dictionary containing detailed coin information
        """
        try:
            trading_pair = f"{symbol}{market}"
            
            # Get 24h stats
            stats = self.get_24h_stats(trading_pair)
            
            # Get recent trades
            trades = self.client.get_recent_trades(symbol=trading_pair, limit=10)
            
            # Get order book
            order_book = self.client.get_order_book(symbol=trading_pair, limit=5)
            
            return {
                'stats': stats,
                'recent_trades': trades,
                'order_book': order_book
            }
        except BinanceAPIException as e:
            logger.error(f"Error fetching detailed info for {symbol}: {e}")
            return {}
