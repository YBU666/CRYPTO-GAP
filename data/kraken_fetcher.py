"""
Kraken exchange data fetcher for CryptoGap+
"""
import pandas as pd
import ccxt
import time
import logging
from typing import Dict, List, Optional

from config.config import KRAKEN_API_KEY, KRAKEN_API_SECRET, TOP_CRYPTOS, MARKETS

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('kraken_fetcher')

class KrakenFetcher:
    """Class to fetch cryptocurrency data from Kraken"""
    
    def __init__(self, api_key: str = KRAKEN_API_KEY, api_secret: str = KRAKEN_API_SECRET):
        """Initialize the Kraken client using ccxt"""
        self.exchange = ccxt.kraken({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
        logger.info("Kraken fetcher initialized")
        
    def get_ticker_prices(self) -> Dict[str, float]:
        """
        Get current prices for all tickers
        
        Returns:
            Dict[str, float]: Dictionary of symbol-price pairs
        """
        try:
            tickers = self.exchange.fetch_tickers()
            return {symbol: ticker['last'] for symbol, ticker in tickers.items() if ticker['last'] is not None}
        except Exception as e:
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
                        
                    # Kraken uses / in symbol names
                    symbol = f"{crypto}/{market}"
                    if symbol in all_prices:
                        row[f"{market}_price"] = all_prices[symbol]
                    else:
                        # Try reverse pair if direct pair doesn't exist
                        reverse_symbol = f"{market}/{crypto}"
                        if reverse_symbol in all_prices:
                            row[f"{market}_price"] = 1 / all_prices[reverse_symbol]
                        else:
                            # Try with Kraken's specific format (e.g., XBT instead of BTC)
                            alt_crypto = 'XBT' if crypto == 'BTC' else crypto
                            alt_market = 'XBT' if market == 'BTC' else market
                                
                            alt_symbol = f"{alt_crypto}/{alt_market}"
                            alt_reverse_symbol = f"{alt_market}/{alt_crypto}"
                            
                            if alt_symbol in all_prices:
                                row[f"{market}_price"] = all_prices[alt_symbol]
                            elif alt_reverse_symbol in all_prices:
                                row[f"{market}_price"] = 1 / all_prices[alt_reverse_symbol]
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
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT')
            
        Returns:
            Dict: Dictionary containing 24h statistics
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': ticker['symbol'],
                'last_price': ticker['last'],
                'bid_price': ticker['bid'],
                'ask_price': ticker['ask'],
                'high_price': ticker['high'],
                'low_price': ticker['low'],
                'volume': ticker['baseVolume'],
                'quote_volume': ticker['quoteVolume'],
                'price_change': ticker.get('change', 0),
                'price_change_percent': ticker.get('percentage', 0),
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
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
            # Handle BTC/XBT conversion for Kraken
            if symbol == 'BTC':
                symbol_for_kraken = 'XBT'
            else:
                symbol_for_kraken = symbol
                
            # Kraken often uses USD instead of USDT
            if market == 'USDT':
                market_alternatives = ['USDT', 'USD']
            else:
                market_alternatives = [market]
                
            # Try different market combinations
            trading_pair = None
            for m in market_alternatives:
                try_pair = f"{symbol_for_kraken}/{m}"
                try:
                    # Check if this pair exists
                    self.exchange.fetch_ticker(try_pair)
                    trading_pair = try_pair
                    break
                except:
                    continue
                    
            if not trading_pair:
                # Try with original symbol as fallback
                for m in market_alternatives:
                    try_pair = f"{symbol}/{m}"
                    try:
                        self.exchange.fetch_ticker(try_pair)
                        trading_pair = try_pair
                        break
                    except:
                        continue
            
            if not trading_pair:
                logger.error(f"Could not find valid trading pair for {symbol}/{market}")
                return {}
            
            # Get 24h stats
            stats = self.get_24h_stats(trading_pair)
            
            # Get recent trades
            trades = self.exchange.fetch_trades(trading_pair, limit=10)
            
            # Get order book
            order_book = self.exchange.fetch_order_book(trading_pair, limit=5)
            
            return {
                'stats': stats,
                'recent_trades': trades,
                'order_book': order_book
            }
        except Exception as e:
            logger.error(f"Error fetching detailed info for {symbol}: {e}")
            return {}
