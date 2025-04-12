"""
Test script for CryptoGap+ application using direct imports
"""
import sys
import os
import pandas as pd
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_cryptogap')

# Import components directly with absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    # Use absolute imports
    import data.binance_fetcher
    import data.bybit_fetcher
    import utils.arbitrage_calculator
    import models.llm_analyzer
    import config.config
    
    # Create instances for testing
    BinanceFetcher = data.binance_fetcher.BinanceFetcher
    BybitFetcher = data.bybit_fetcher.BybitFetcher
    ArbitrageCalculator = utils.arbitrage_calculator.ArbitrageCalculator
    LLMAnalyzer = models.llm_analyzer.LLMAnalyzer
    TOP_CRYPTOS = config.config.TOP_CRYPTOS
    MARKETS = config.config.MARKETS
    
    logger.info("Successfully imported all modules")
except Exception as e:
    logger.error(f"Error importing modules: {e}")
    sys.exit(1)

def test_binance_fetcher():
    """Test Binance data fetcher functionality"""
    logger.info("Testing Binance fetcher...")
    
    try:
        fetcher = BinanceFetcher()
        logger.info("Binance fetcher initialized")
        
        # Test ticker prices
        prices = fetcher.get_ticker_prices()
        logger.info(f"Got {len(prices)} ticker prices from Binance")
        
        # Test top crypto prices
        df = fetcher.get_top_crypto_prices()
        logger.info(f"Got top crypto prices from Binance: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Test 24h stats for BTC/USDT
        stats = fetcher.get_24h_stats("BTCUSDT")
        logger.info(f"Got 24h stats for BTCUSDT: {len(stats)} data points")
        
        # Test detailed coin info
        info = fetcher.get_detailed_coin_info("BTC", "USDT")
        logger.info(f"Got detailed info for BTC/USDT: {len(info)} sections")
        
        logger.info("Binance fetcher tests passed")
        return True
    except Exception as e:
        logger.error(f"Binance fetcher test failed: {e}")
        return False

def test_bybit_fetcher():
    """Test Bybit data fetcher functionality"""
    logger.info("Testing Bybit fetcher...")
    
    try:
        fetcher = BybitFetcher()
        logger.info("Bybit fetcher initialized")
        
        # Test ticker prices
        prices = fetcher.get_ticker_prices()
        logger.info(f"Got {len(prices)} ticker prices from Bybit")
        
        # Test top crypto prices
        df = fetcher.get_top_crypto_prices()
        logger.info(f"Got top crypto prices from Bybit: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Test 24h stats for BTC/USDT
        stats = fetcher.get_24h_stats("BTC/USDT")
        logger.info(f"Got 24h stats for BTC/USDT: {len(stats)} data points")
        
        # Test detailed coin info
        info = fetcher.get_detailed_coin_info("BTC", "USDT")
        logger.info(f"Got detailed info for BTC/USDT: {len(info)} sections")
        
        logger.info("Bybit fetcher tests passed")
        return True
    except Exception as e:
        logger.error(f"Bybit fetcher test failed: {e}")
        return False

def test_arbitrage_calculator():
    """Test arbitrage calculator functionality"""
    logger.info("Testing arbitrage calculator...")
    
    try:
        calculator = ArbitrageCalculator()
        logger.info("Arbitrage calculator initialized")
        
        # Test fetching all prices
        binance_prices, bybit_prices = calculator.fetch_all_prices()
        logger.info(f"Got prices from both exchanges: Binance {binance_prices.shape}, Bybit {bybit_prices.shape}")
        
        # Test calculating arbitrage opportunities
        opportunities = calculator.calculate_arbitrage_opportunities()
        logger.info(f"Found {len(opportunities)} arbitrage opportunities")
        
        # Test low price gainers
        gainers = calculator.get_low_price_gainers()
        logger.info(f"Found {len(gainers)} low price gainers")
        
        # Test trade profit calculation
        profit = calculator.calculate_trade_profit("BTC", "USDT", 100.0, "Binance", "Bybit")
        logger.info(f"Calculated trade profit: {profit.get('profit', 'N/A')}")
        
        # Test last opportunity
        last = calculator.get_last_opportunity()
        logger.info(f"Last opportunity: {last}")
        
        logger.info("Arbitrage calculator tests passed")
        return True
    except Exception as e:
        logger.error(f"Arbitrage calculator test failed: {e}")
        return False

def test_llm_analyzer():
    """Test LLM analyzer functionality"""
    logger.info("Testing LLM analyzer...")
    
    try:
        # Skip actual API calls if no API key is set
        OPENAI_API_KEY = config.config.OPENAI_API_KEY
        
        if not OPENAI_API_KEY:
            logger.warning("Skipping LLM tests as no API key is set")
            return True
        
        analyzer = LLMAnalyzer()
        logger.info("LLM analyzer initialized")
        
        # Create a sample opportunity for testing
        opportunity = {
            'Symbol': 'BTC',
            'Market': 'USDT',
            'Buy_Exchange': 'Binance',
            'Sell_Exchange': 'Bybit',
            'Buy_Price': 50000.0,
            'Sell_Price': 50100.0,
            'Price_Diff_Pct': 0.2,
            'Profit_After_Fees_Pct': 0.1
        }
        
        # Test arbitrage opportunity analysis
        analysis = analyzer.analyze_arbitrage_opportunity(opportunity)
        logger.info(f"Generated arbitrage analysis: {len(analysis)} characters")
        
        # Create a sample gainer for testing
        gainer = {
            'Symbol': 'XRP',
            'Binance_Price': 0.5,
            'Bybit_Price': 0.51,
            'Price_Diff_Pct': 2.0,
            'Avg_Price': 0.505
        }
        
        # Test low price gainer analysis
        analysis = analyzer.analyze_low_price_gainer(gainer)
        logger.info(f"Generated low price gainer analysis: {len(analysis)} characters")
        
        # Create sample coin data for testing
        coin_data = {
            'stats': {
                'symbol': 'BTCUSDT',
                'price_change': 100.0,
                'price_change_percent': 0.2,
                'weighted_avg_price': 50050.0,
                'last_price': 50100.0,
                'high_price': 50200.0,
                'low_price': 49900.0,
                'volume': 100.0,
                'quote_volume': 5000000.0
            },
            'recent_trades': [
                {'price': 50100.0, 'qty': 0.1, 'isBuyerMaker': False},
                {'price': 50090.0, 'qty': 0.2, 'isBuyerMaker': True}
            ],
            'order_book': {
                'bids': [[50000.0, 1.0], [49990.0, 2.0]],
                'asks': [[50100.0, 1.0], [50110.0, 2.0]]
            }
        }
        
        # Test coin analysis
        analysis = analyzer.generate_coin_analysis('BTC', coin_data)
        logger.info(f"Generated coin analysis: {len(analysis)} characters")
        
        logger.info("LLM analyzer tests passed")
        return True
    except Exception as e:
        logger.error(f"LLM analyzer test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    logger.info("Starting CryptoGap+ tests")
    
    results = {
        "Binance Fetcher": test_binance_fetcher(),
        "Bybit Fetcher": test_bybit_fetcher(),
        "Arbitrage Calculator": test_arbitrage_calculator(),
        "LLM Analyzer": test_llm_analyzer()
    }
    
    # Print summary
    logger.info("Test Results Summary:")
    all_passed = True
    
    for test, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        logger.info(f"{test}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("All tests passed successfully!")
    else:
        logger.error("Some tests failed. Check logs for details.")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()
