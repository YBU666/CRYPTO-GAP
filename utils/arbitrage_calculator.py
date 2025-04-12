"""
Data integration and arbitrage calculation module for CryptoGap+
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
import time

from data.binance_fetcher import BinanceFetcher
from data.kraken_fetcher import KrakenFetcher
from config.config import TOP_CRYPTOS, MARKETS, BINANCE_TAKER_FEE, KRAKEN_TAKER_FEE, SLIPPAGE

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('arbitrage_calculator')

class ArbitrageCalculator:
    """Class to calculate arbitrage opportunities between exchanges"""
    
    def __init__(self):
        """Initialize the arbitrage calculator with exchange fetchers"""
        self.binance = BinanceFetcher()
        self.kraken = KrakenFetcher()
        self.last_opportunity = None
        logger.info("Arbitrage calculator initialized")
    
    def fetch_all_prices(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Fetch prices from both exchanges
        
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: DataFrames with prices from Binance and Kraken
        """
        binance_prices = self.binance.get_top_crypto_prices()
        kraken_prices = self.kraken.get_top_crypto_prices()
        return binance_prices, kraken_prices
    
    def calculate_arbitrage_opportunities(self) -> pd.DataFrame:
        """
        Calculate arbitrage opportunities between Binance and Kraken
        
        Returns:
            pd.DataFrame: DataFrame with arbitrage opportunities
        """
        try:
            # Fetch prices from both exchanges
            binance_prices, kraken_prices = self.fetch_all_prices()
            
            if binance_prices.empty or kraken_prices.empty:
                logger.warning("Failed to fetch prices from one or both exchanges")
                return pd.DataFrame()
            
            # Merge dataframes on Symbol
            merged_df = pd.merge(
                binance_prices, 
                kraken_prices, 
                on='Symbol', 
                suffixes=('_binance', '_kraken')
            )
            
            # Calculate arbitrage opportunities
            opportunities = []
            
            for _, row in merged_df.iterrows():
                symbol = row['Symbol']
                
                for market in MARKETS:
                    if symbol == market:
                        continue
                    
                    binance_col = f"{market}_price_binance"
                    kraken_col = f"{market}_price_kraken"
                    
                    # Skip if either price is missing
                    if pd.isna(row.get(binance_col)) or pd.isna(row.get(kraken_col)):
                        continue
                    
                    binance_price = row[binance_col]
                    kraken_price = row[kraken_col]
                    
                    # Calculate price difference percentage
                    price_diff_pct = abs(binance_price - kraken_price) / min(binance_price, kraken_price) * 100
                    
                    # Determine buy/sell exchanges based on price
                    if binance_price < kraken_price:
                        buy_exchange = "Binance"
                        sell_exchange = "Kraken"
                        buy_price = binance_price
                        sell_price = kraken_price
                    else:
                        buy_exchange = "Kraken"
                        sell_exchange = "Binance"
                        buy_price = kraken_price
                        sell_price = binance_price
                    
                    # Include all opportunities with a price difference
                    if price_diff_pct > 0:
                        opportunities.append({
                            'Symbol': symbol,
                            'Market': market,
                            'Buy_Exchange': buy_exchange,
                            'Sell_Exchange': sell_exchange,
                            'Buy_Price': buy_price,
                            'Sell_Price': sell_price,
                            'Price_Diff_Pct': price_diff_pct,
                            'Timestamp': time.time()
                        })
            
            # Create DataFrame from opportunities
            opportunities_df = pd.DataFrame(opportunities)
            
            # Sort by price difference percentage (descending)
            if not opportunities_df.empty:
                opportunities_df = opportunities_df.sort_values(by='Price_Diff_Pct', ascending=False)
                
                # Store the best opportunity as the last seen
                if len(opportunities_df) > 0:
                    self.last_opportunity = opportunities_df.iloc[0].to_dict()
            
            return opportunities_df
        
        except Exception as e:
            logger.error(f"Error calculating arbitrage opportunities: {e}")
            return pd.DataFrame()
    
    def get_low_price_gainers(self) -> pd.DataFrame:
        """
        Identify coins with low prices that have potential for gains
        
        Returns:
            pd.DataFrame: DataFrame with low price gainers
        """
        try:
            # Fetch prices from both exchanges
            binance_prices, kraken_prices = self.fetch_all_prices()
            
            if binance_prices.empty or kraken_prices.empty:
                logger.warning("Failed to fetch prices from one or both exchanges")
                return pd.DataFrame()
            
            # Focus on USDT pairs for price comparison
            usdt_col_binance = 'USDT_price_binance'
            usdt_col_kraken = 'USDT_price_kraken'
            
            # Merge dataframes on Symbol
            merged_df = pd.merge(
                binance_prices, 
                kraken_prices, 
                on='Symbol', 
                suffixes=('_binance', '_kraken')
            )
            
            # Filter for coins with price < $1 on either exchange
            low_price_df = merged_df[
                ((merged_df[usdt_col_binance] < 1) | (merged_df[usdt_col_kraken] < 1)) &
                (~pd.isna(merged_df[usdt_col_binance])) & 
                (~pd.isna(merged_df[usdt_col_kraken]))
            ].copy()
            
            if low_price_df.empty:
                return pd.DataFrame()
            
            # Calculate price difference percentage
            low_price_df['Price_Diff_Pct'] = (
                (low_price_df[usdt_col_binance] - low_price_df[usdt_col_kraken]).abs() / 
                low_price_df[[usdt_col_binance, usdt_col_kraken]].min(axis=1) * 100
            )
            
            # Calculate average price
            low_price_df['Avg_Price'] = low_price_df[[usdt_col_binance, usdt_col_kraken]].mean(axis=1)
            
            # Sort by price difference percentage (descending)
            low_price_df = low_price_df.sort_values(by='Price_Diff_Pct', ascending=False)
            
            # Select relevant columns
            result_df = low_price_df[[
                'Symbol', 
                usdt_col_binance, 
                usdt_col_kraken, 
                'Price_Diff_Pct', 
                'Avg_Price'
            ]].rename(columns={
                usdt_col_binance: 'Binance_Price',
                usdt_col_kraken: 'Kraken_Price'
            })
            
            return result_df
        
        except Exception as e:
            logger.error(f"Error identifying low price gainers: {e}")
            return pd.DataFrame()
    
    def calculate_trade_profit(self, symbol: str, market: str, amount: float, 
                              buy_exchange: str, sell_exchange: str) -> Dict:
        """
        Calculate potential profit for a specific trade without fees or slippage
        
        Args:
            symbol (str): Cryptocurrency symbol (e.g., 'BTC')
            market (str): Market to trade against (e.g., 'USDT')
            amount (float): Amount to trade in the market currency
            buy_exchange (str): Exchange to buy from ('Binance' or 'Kraken')
            sell_exchange (str): Exchange to sell on ('Binance' or 'Kraken')
            
        Returns:
            Dict: Dictionary with trade profit details
        """
        try:
            # Fetch latest prices
            binance_prices, kraken_prices = self.fetch_all_prices()
            
            if binance_prices.empty or kraken_prices.empty:
                logger.warning("Failed to fetch prices from one or both exchanges")
                return {}
            
            # Get prices for the specified symbol and market
            binance_price = binance_prices[
                binance_prices['Symbol'] == symbol
            ][f"{market}_price"].values[0]
            
            kraken_price = kraken_prices[
                kraken_prices['Symbol'] == symbol
            ][f"{market}_price"].values[0]
            
            # Determine buy and sell prices based on specified exchanges
            buy_price = binance_price if buy_exchange == 'Binance' else kraken_price
            sell_price = binance_price if sell_exchange == 'Binance' else kraken_price
            
            # Calculate trade details
            crypto_amount = amount / buy_price
            sell_amount = crypto_amount * sell_price
            
            final_amount = sell_amount
            profit = final_amount - amount
            profit_percentage = (profit / amount) * 100
            
            return {
                'symbol': symbol,
                'market': market,
                'initial_investment': amount,
                'buy_exchange': buy_exchange,
                'buy_price': buy_price,
                'crypto_amount': crypto_amount,
                'sell_exchange': sell_exchange,
                'sell_price': sell_price,
                'sell_amount': sell_amount,
                'final_amount': final_amount,
                'profit': profit,
                'profit_percentage': profit_percentage,
                'profitable': profit > 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating trade profit: {e}")
            return {}
    
    def get_last_opportunity(self) -> Dict:
        """
        Get the last seen arbitrage opportunity
        
        Returns:
            Dict: Dictionary with last seen opportunity details
        """
        return self.last_opportunity if self.last_opportunity else {}
