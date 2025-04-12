"""
LLM integration module for CryptoGap+
"""
import logging
from typing import Dict, List, Optional
import json
import time
from groq import Groq

from config.config import GROQ_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('llm_analyzer')

class LLMAnalyzer:
    """Class to analyze crypto data using Groq"""
    
    def __init__(self, api_key: str = GROQ_API_KEY):
        """Initialize the Groq client"""
        self.client = Groq(
            api_key=api_key
        )
        logger.info("LLM Analyzer initialized with Groq")
    
    def analyze_arbitrage_opportunity(self, opportunity: Dict) -> str:
        """
        Analyze an arbitrage opportunity and provide insights
        
        Args:
            opportunity (Dict): Dictionary containing arbitrage opportunity details
            
        Returns:
            str: LLM-generated analysis and insights
        """
        try:
            if not opportunity:
                return "No arbitrage opportunity data provided."
            
            # Create a prompt for the LLM
            prompt = f"""
            Analyze the following cryptocurrency arbitrage opportunity:
            
            Symbol: {opportunity.get('Symbol')}
            Market: {opportunity.get('Market')}
            Buy Exchange: {opportunity.get('Buy_Exchange')}
            Sell Exchange: {opportunity.get('Sell_Exchange')}
            Buy Price: {opportunity.get('Buy_Price')}
            Sell Price: {opportunity.get('Sell_Price')}
            Price Difference: {opportunity.get('Price_Diff_Pct', 0):.2f}%
            Profit After Fees: {opportunity.get('Profit_After_Fees_Pct', 0):.2f}%
            
            Please provide:
            1. A brief explanation of why this arbitrage opportunity might exist
            2. Potential risks associated with this trade
            3. Recommendations on timing and execution
            4. Any other relevant insights for a trader
            
            Keep your response concise and trader-friendly.
            """
            
            # Call the Groq API
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a cryptocurrency trading expert specializing in arbitrage opportunities. Provide concise, practical insights for traders."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract and return the analysis
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error analyzing arbitrage opportunity: {e}")
            return f"Error analyzing opportunity: {str(e)}"
    
    def analyze_low_price_gainer(self, gainer_data: Dict) -> str:
        """
        Analyze a low-price gainer and provide insights
        
        Args:
            gainer_data (Dict): Dictionary containing low-price gainer details
            
        Returns:
            str: LLM-generated analysis and insights
        """
        try:
            if not gainer_data:
                return "No low-price gainer data provided."
            
            # Create a prompt for the LLM
            prompt = f"""
            Analyze the following low-price cryptocurrency with price discrepancy:
            
            Symbol: {gainer_data.get('Symbol')}
            Binance Price: ${gainer_data.get('Binance_Price', 0):.6f}
            Kraken Price: ${gainer_data.get('Kraken_Price', 0):.6f}
            Price Difference: {gainer_data.get('Price_Diff_Pct', 0):.2f}%
            Average Price: ${gainer_data.get('Avg_Price', 0):.6f}
            
            Please provide:
            1. Potential reasons for this price discrepancy in a low-priced coin
            2. Opportunities this might present for traders
            3. Risks associated with trading low-priced cryptocurrencies
            4. A brief recommendation on whether this is worth investigating further
            
            Keep your response concise and trader-friendly.
            """
            
            # Call the Groq API
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a cryptocurrency trading expert specializing in market inefficiencies and low-cap coins. Provide concise, practical insights for traders."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract and return the analysis
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error analyzing low-price gainer: {e}")
            return f"Error analyzing low-price gainer: {str(e)}"
    
    def generate_coin_analysis(self, symbol: str, coin_data: Dict) -> str:
        """
        Generate a detailed analysis for a specific coin
        
        Args:
            symbol (str): Coin symbol (e.g., 'BTC')
            coin_data (Dict): Dictionary containing detailed coin information
            
        Returns:
            str: LLM-generated detailed coin analysis
        """
        try:
            if not coin_data:
                return f"No data available for {symbol}."
            
            # Extract relevant data
            stats = coin_data.get('stats', {})
            recent_trades = coin_data.get('recent_trades', [])
            order_book = coin_data.get('order_book', {})
            
            # Format data for the prompt
            stats_str = json.dumps(stats, indent=2)
            
            # Summarize recent trades
            trades_summary = "Recent Trades:\n"
            for i, trade in enumerate(recent_trades[:5]):
                price = trade.get('price', 0)
                quantity = trade.get('qty', 0)
                side = trade.get('isBuyerMaker', False)
                side_str = "Sell" if side else "Buy"
                trades_summary += f"- {side_str} {quantity} at {price}\n"
            
            # Summarize order book
            bids = order_book.get('bids', [])
            asks = order_book.get('asks', [])
            
            order_book_summary = "Order Book:\n"
            order_book_summary += "Top 3 Bids:\n"
            for i, bid in enumerate(bids[:3]):
                order_book_summary += f"- Price: {bid[0]}, Quantity: {bid[1]}\n"
            
            order_book_summary += "Top 3 Asks:\n"
            for i, ask in enumerate(asks[:3]):
                order_book_summary += f"- Price: {ask[0]}, Quantity: {ask[1]}\n"
            
            # Create a prompt for the LLM
            prompt = f"""
            Generate a detailed analysis for {symbol} based on the following data:
            
            24-Hour Statistics:
            {stats_str}
            
            {trades_summary}
            
            {order_book_summary}
            
            Please provide:
            1. A summary of the current market conditions for {symbol}
            2. Price trend analysis based on the 24-hour statistics
            3. Trading volume analysis and what it indicates
            4. Order book analysis (liquidity, buy/sell pressure)
            5. Short-term price outlook (next 24-48 hours)
            6. Potential trading strategies based on this data
            
            Keep your response comprehensive but trader-friendly.
            """
            
            # Call the Groq API
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are a cryptocurrency analyst specializing in {symbol} trading. Provide detailed, data-driven analysis for traders."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            # Extract and return the analysis
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating coin analysis: {e}")
            return f"Error generating analysis for {symbol}: {str(e)}"
