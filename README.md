# CryptoGap+

## Advanced Crypto Arbitrage & Analysis Tool

CryptoGap+ is an advanced cryptocurrency arbitrage and analysis tool that helps traders identify profitable trading opportunities across exchanges. The application fetches live prices for top cryptocurrencies from Binance and Kraken, calculates arbitrage opportunities, and provides AI-powered insights using Groq.

![CryptoGap+ Logo](https://img.icons8.com/color/96/000000/cryptocurrency.png)

## Features

- **Live Price Tracking**: Monitor real-time prices of top cryptocurrencies (BTC, ETH, SOL, etc.) from Binance and Kraken
- **Arbitrage Detection**: Automatically identify price discrepancies across exchanges and markets (USDT, BTC, BNB)
- **AI-Powered Analysis**: Get human-like insights on arbitrage opportunities using Groq
- **Low-Price Gainer Detection**: Find low-priced coins with significant price differences between exchanges
- **Trade Simulator**: Calculate potential profits after fees and slippage
- **Opportunity Tracking**: Keep track of the last seen arbitrage opportunity
- **Detailed Coin Analysis**: Get comprehensive analysis for specific coins including price trends and trading volume

## Installation

### Prerequisites

- Python 3.10+
- Binance API key and secret (optional)
- Kraken API key and secret (optional)
- Groq API key

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/cryptogap-plus.git
   cd cryptogap-plus
   ```

2. Install required packages:
   ```
   pip install streamlit openai pandas python-binance ccxt python-dotenv plotly
   ```

3. Create a `.env` file in the project root directory with your API keys:
   ```
   # Binance API credentials
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_API_SECRET=your_binance_api_secret

   # Kraken API credentials
   KRAKEN_API_KEY=your_kraken_api_key
   KRAKEN_API_SECRET=your_kraken_api_secret

   # Groq API key
   GROQ_API_KEY=your_groq_api_key
   ```

   Note: The application can run without API keys, but some features may be limited.

## Usage

1. Start the Streamlit application:
   ```
   streamlit run app.py
   ```

2. The application will open in your default web browser at `http://localhost:8501`

3. Use the sidebar to:
   - Refresh data
   - Select specific coins for detailed analysis
   - Configure the trade simulator

4. Navigate through the tabs to access different features:
   - **Arbitrage Opportunities**: View current arbitrage opportunities with AI analysis
   - **Live Prices**: Monitor real-time prices across exchanges
   - **Low-Price Gainers**: Discover low-priced coins with potential
   - **Detailed Analysis**: Get comprehensive analysis for selected coins

## Project Structure

```
CryptoGap+/
├── app.py                  # Main Streamlit application
├── config/
│   ├── __init__.py
│   └── config.py           # Configuration settings
├── data/
│   ├── __init__.py
│   ├── binance_fetcher.py  # Binance data fetcher
│   └── kraken_fetcher.py   # Kraken data fetcher
├── models/
│   ├── __init__.py
│   └── llm_analyzer.py     # Groq integration
├── utils/
│   ├── __init__.py
│   └── arbitrage_calculator.py  # Arbitrage calculation logic
└── tests/
    ├── __init__.py
    ├── test_cryptogap.py   # Comprehensive tests
    └── simple_test.py      # Simple structure tests
```

## Configuration

You can modify the following settings in `config/config.py`:

- `TOP_CRYPTOS`: List of cryptocurrencies to track
- `MARKETS`: Markets to compare for arbitrage (USDT, BTC, BNB)
- `BINANCE_TAKER_FEE`: Fee percentage for Binance
- `KRAKEN_TAKER_FEE`: Fee percentage for Kraken
- `SLIPPAGE`: Expected slippage percentage
- `REFRESH_RATE`: Data refresh rate in seconds

## Limitations

- The application uses public API endpoints with rate limits
- Arbitrage opportunities may not be actionable due to market conditions
- LLM analysis requires a Groq API key and may incur costs

## Future Enhancements

- Add support for more exchanges
- Implement historical arbitrage data analysis
- Create automated trading functionality
- Add more advanced technical indicators
- Implement real-time alerts for profitable opportunities

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Binance and Kraken for providing API access
- Groq for the powerful language model capabilities
- Streamlit for the intuitive UI framework

---

Created with ❤️ for crypto traders and enthusiasts
