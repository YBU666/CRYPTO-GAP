"""
Configuration settings for CryptoGap+
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Exchange API keys
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY", "")
KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET", "")

# Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Top cryptocurrencies to track (available on both Binance and Kraken)
TOP_CRYPTOS = [
    "BTC", "ETH", "SOL", "BNB", "XRP",
    "ADA", "DOGE", "DOT", "LINK", "LTC"
]

# Markets to compare for arbitrage
MARKETS = ["USDT", "BTC"]

# Fee settings
BINANCE_TAKER_FEE = 0.001  # 0.1%
KRAKEN_TAKER_FEE = 0.0026  # 0.26%
SLIPPAGE = 0.002           # 0.2%

# Refresh rate in seconds
REFRESH_RATE = 60
