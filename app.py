"""
Main Streamlit application for CryptoGap+
"""
import streamlit as st
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime

from utils.arbitrage_calculator import ArbitrageCalculator
from models.llm_analyzer import LLMAnalyzer
from data.binance_fetcher import BinanceFetcher
from data.kraken_fetcher import KrakenFetcher
from config.config import TOP_CRYPTOS, MARKETS, REFRESH_RATE

# Initialize components
arbitrage_calculator = ArbitrageCalculator()
llm_analyzer = LLMAnalyzer()
binance_fetcher = BinanceFetcher()
kraken_fetcher = KrakenFetcher()

# Page configuration
st.set_page_config(
    page_title="CryptoGap+ | Crypto Arbitrage Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* General styles */
    .main-header {
        font-size: 2.5rem;
        color: #2196F3;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .header-image {
        height: 45px;
        width: 80px;
        object-fit: cover;
        border-radius: 8px;
        vertical-align: middle;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #FFFFFF;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    /* Card styles */
    .card {
        background-color: #1E1E1E;
        color: #E0E0E0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    
    /* Profit/Loss indicators */
    .profit {
        color: #00E676;
        font-weight: bold;
        background-color: rgba(0, 230, 118, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
    }
    .loss {
        color: #FF1744;
        font-weight: bold;
        background-color: rgba(255, 23, 68, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
    }
    .info {
        color: #2196F3;
        font-weight: bold;
        background-color: rgba(33, 150, 243, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    /* Highlight box */
    .highlight {
        background-color: #2C2C2C;
        color: #E0E0E0;
        padding: 15px;
        border-left: 5px solid #FFC107;
        margin-bottom: 15px;
        border-radius: 0 10px 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Table styles */
    .dataframe {
        background-color: #1E1E1E !important;
        color: #E0E0E0 !important;
    }
    .dataframe th {
        background-color: #2C2C2C !important;
        color: #2196F3 !important;
    }
    .dataframe td {
        background-color: #1E1E1E !important;
        color: #E0E0E0 !important;
    }
    
    /* Metric styles */
    [data-testid="stMetricValue"] {
        color: #2196F3 !important;
    }
    [data-testid="stMetricDelta"] {
        color: #00E676 !important;
    }
    
    /* LLM Analysis section */
    .llm-analysis {
        background-color: #2C2C2C;
        color: #E0E0E0;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #424242;
        margin: 15px 0;
    }
    .llm-analysis h3 {
        color: #2196F3;
        margin-bottom: 15px;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1E1E1E;
    }
    ::-webkit-scrollbar-thumb {
        background: #424242;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown('<div class="main-header"><img src="https://variety.com/wp-content/uploads/2021/12/Bitcoin-Cryptocurrency-Placeholder.jpg?w=1000&h=563&crop=1" class="header-image" alt="CryptoGap+ Logo">CryptoGap+</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Advanced Crypto Arbitrage & Analysis Tool</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Controls & Settings")

# Refresh button
if st.sidebar.button("Refresh Data"):
    st.experimental_rerun()

# Coin selection for detailed analysis
st.sidebar.markdown("## Detailed Coin Analysis")
selected_coin = st.sidebar.selectbox("Select Coin", TOP_CRYPTOS)
selected_market = st.sidebar.selectbox("Select Market", MARKETS)

# Trade simulator
st.sidebar.markdown("## Trade Simulator")
trade_amount = st.sidebar.number_input("Investment Amount (USDT)", min_value=10.0, max_value=10000.0, value=100.0, step=10.0)
buy_exchange = st.sidebar.radio("Buy Exchange", ["Binance", "Kraken"])
sell_exchange = "Kraken" if buy_exchange == "Binance" else "Binance"

# Main content area - using tabs
tab1, tab2, tab3, tab4 = st.tabs(["Arbitrage Opportunities", "Live Prices", "Low-Price Gainers", "Detailed Analysis"])

with tab1:
    st.markdown("## Arbitrage Opportunities")
    
    with st.spinner("Calculating arbitrage opportunities..."):
        # Get arbitrage opportunities
        opportunities_df = arbitrage_calculator.calculate_arbitrage_opportunities()
        
        if not opportunities_df.empty:
            # Display opportunities table
            st.dataframe(
                opportunities_df[['Symbol', 'Market', 'Buy_Exchange', 'Sell_Exchange', 
                                 'Buy_Price', 'Sell_Price', 'Price_Diff_Pct']]
                .style.format({
                    'Buy_Price': '${:.6f}',
                    'Sell_Price': '${:.6f}',
                    'Price_Diff_Pct': '{:.2f}%'
                }).map(lambda x: f'color: {"#00E676" if x > 0 else "#FF1744"}' if isinstance(x, float) else '', subset=['Price_Diff_Pct'])
            )
            
            # Get the best opportunity
            best_opportunity = opportunities_df.iloc[0].to_dict()
            
            # LLM analysis of the best opportunity
            st.markdown("### LLM Analysis of Best Opportunity")
            with st.spinner("Generating analysis..."):
                analysis = llm_analyzer.analyze_arbitrage_opportunity(best_opportunity)
                st.markdown(f'<div class="llm-analysis">{analysis}</div>', unsafe_allow_html=True)
            
            # Last seen opportunity tracker
            st.markdown("### Last Seen Opportunity")
            last_opportunity = arbitrage_calculator.get_last_opportunity()
            if last_opportunity:
                timestamp = last_opportunity.get('Timestamp', time.time())
                formatted_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                price_diff = last_opportunity.get('Price_Diff_Pct', 0)
                diff_color = '#00E676' if price_diff > 0 else '#FF1744'
                
                st.markdown(f"""
                <div class="highlight">
                Last seen: {formatted_time}<br>
                Symbol: {last_opportunity.get('Symbol')}/{last_opportunity.get('Market')}<br>
                Buy on {last_opportunity.get('Buy_Exchange')} at ${last_opportunity.get('Buy_Price', 0):.6f}<br>
                Sell on {last_opportunity.get('Sell_Exchange')} at ${last_opportunity.get('Sell_Price', 0):.6f}<br>
                Price Difference: <span style="color: {diff_color}">{price_diff:.2f}%</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No profitable arbitrage opportunities found at the moment. Try refreshing later.")

with tab2:
    st.markdown("## Live Prices")
    
    with st.spinner("Fetching live prices..."):
        # Get prices from both exchanges
        binance_prices, kraken_prices = arbitrage_calculator.fetch_all_prices()
        
        if not binance_prices.empty and not kraken_prices.empty:
            # Merge dataframes
            merged_df = pd.merge(
                binance_prices, 
                kraken_prices, 
                on='Symbol', 
                suffixes=('_binance', '_kraken')
            )
            
            # Display prices
            for market in MARKETS:
                st.markdown(f"### {market} Market")
                
                market_df = merged_df[['Symbol', f'{market}_price_binance', f'{market}_price_kraken']].copy()
                market_df = market_df.dropna()
                
                if not market_df.empty:
                    # Calculate price difference
                    market_df['Price_Diff_Pct'] = (
                        (market_df[f'{market}_price_binance'] - market_df[f'{market}_price_kraken']).abs() / 
                        market_df[[f'{market}_price_binance', f'{market}_price_kraken']].min(axis=1) * 100
                    )
                    
                    # Rename columns for display
                    market_df = market_df.rename(columns={
                        f'{market}_price_binance': 'Binance Price',
                        f'{market}_price_kraken': 'Kraken Price'
                    })
                    
                    # Display table with colored price differences
                    st.dataframe(
                        market_df.style.format({
                            'Binance Price': '${:.6f}',
                            'Kraken Price': '${:.6f}',
                            'Price_Diff_Pct': '{:.2f}%'
                        }).map(lambda x: f'color: {"#00E676" if x > 0 else "#FF1744"}' if isinstance(x, float) else '', subset=['Price_Diff_Pct'])
                    )
                else:
                    st.info(f"No data available for {market} market.")
        else:
            st.error("Failed to fetch prices from one or both exchanges.")

with tab3:
    st.markdown("## Low-Price Gainers")
    
    with st.spinner("Identifying low-price gainers..."):
        # Get low-price gainers
        gainers_df = arbitrage_calculator.get_low_price_gainers()
        
        if not gainers_df.empty:
            # Display gainers table with colored price differences
            st.dataframe(
                gainers_df.style.format({
                    'Binance_Price': '${:.6f}',
                    'Kraken_Price': '${:.6f}',
                    'Price_Diff_Pct': '{:.2f}%',
                    'Avg_Price': '${:.6f}'
                }).map(lambda x: f'color: {"#00E676" if x > 0 else "#FF1744"}' if isinstance(x, float) else '', subset=['Price_Diff_Pct'])
            )
            
            # Get the top gainer
            top_gainer = gainers_df.iloc[0].to_dict()
            
            # LLM analysis of the top gainer
            st.markdown("### LLM Analysis of Top Low-Price Gainer")
            with st.spinner("Generating analysis..."):
                analysis = llm_analyzer.analyze_low_price_gainer(top_gainer)
                st.markdown(f'<div class="card">{analysis}</div>', unsafe_allow_html=True)
        else:
            st.info("No low-price gainers found at the moment. Try refreshing later.")

with tab4:
    st.markdown(f"## Detailed Analysis: {selected_coin}/{selected_market}")
    
    with st.spinner(f"Fetching detailed data for {selected_coin}..."):
        # Get detailed coin info from both exchanges
        binance_info = binance_fetcher.get_detailed_coin_info(selected_coin, selected_market)
        kraken_info = kraken_fetcher.get_detailed_coin_info(selected_coin, selected_market)
        
        if binance_info and 'stats' in binance_info:
            # Display basic stats
            binance_stats = binance_info['stats']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Current Price", 
                    f"${float(binance_stats.get('last_price', 0)):.6f}", 
                    f"{float(binance_stats.get('price_change_percent', 0)):.2f}%"
                )
            
            with col2:
                st.metric(
                    "24h High", 
                    f"${float(binance_stats.get('high_price', 0)):.6f}"
                )
            
            with col3:
                st.metric(
                    "24h Low", 
                    f"${float(binance_stats.get('low_price', 0)):.6f}"
                )
            
            col4, col5, col6 = st.columns(3)
            
            with col4:
                st.metric(
                    "24h Volume", 
                    f"{float(binance_stats.get('volume', 0)):.2f} {selected_coin}"
                )
            
            with col5:
                st.metric(
                    "24h Quote Volume", 
                    f"${float(binance_stats.get('quote_volume', 0)):.2f}"
                )
            
            with col6:
                st.metric(
                    "Trade Count", 
                    f"{int(binance_stats.get('count', 0))}"
                )
            
            # Create price chart
            if 'open_price' in binance_stats and 'high_price' in binance_stats and 'low_price' in binance_stats and 'last_price' in binance_stats:
                fig = go.Figure(data=[go.Candlestick(
                    x=['Open', 'High', 'Low', 'Close'],
                    open=[float(binance_stats['open_price'])] * 4,
                    high=[float(binance_stats['high_price'])] * 4,
                    low=[float(binance_stats['low_price'])] * 4,
                    close=[float(binance_stats['last_price'])] * 4
                )])
                
                fig.update_layout(
                    title=f"{selected_coin}/{selected_market} 24h Price Range",
                    xaxis_title="Price Points",
                    yaxis_title="Price",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # LLM analysis
            st.markdown("### LLM Analysis")
            with st.spinner("Generating analysis..."):
                analysis = llm_analyzer.generate_coin_analysis(selected_coin, binance_info)
                st.markdown(f'<div class="card">{analysis}</div>', unsafe_allow_html=True)
            
            # Trade simulator results
            st.markdown("### Trade Simulator Results")
            with st.spinner("Calculating trade simulation..."):
                trade_result = arbitrage_calculator.calculate_trade_profit(
                    selected_coin, selected_market, trade_amount, buy_exchange, sell_exchange
                )
                
                if trade_result:
                    profit = trade_result.get('profit', 0)
                    profit_class = "profit" if profit > 0 else "loss"
                    
                    st.markdown(f"""
                    <div class="card">
                        <h4>Trade Simulation: {selected_coin}/{selected_market}</h4>
                        <p>Investment: ${trade_amount:.2f}</p>
                        <p>Buy on {buy_exchange} at ${trade_result.get('buy_price', 0):.6f}</p>
                        <p>Sell on {sell_exchange} at ${trade_result.get('sell_price', 0):.6f}</p>
                        <p>Crypto amount: {trade_result.get('crypto_amount', 0):.6f} {selected_coin}</p>
                        <p>Final amount: ${trade_result.get('final_amount', 0):.2f}</p>
                        <p>Profit: <span class="{profit_class}">${profit:.2f} (<span style="color: {'#00E676' if profit > 0 else '#FF1744'}">{trade_result.get('profit_percentage', 0):.2f}%</span>)</span></p>
                        <p>Recommendation: <span class="info">{
                            "Consider this trade" if profit > 0 else "Avoid this trade"
                        }</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Failed to calculate trade simulation.")
        else:
            st.error(f"Failed to fetch detailed information for {selected_coin}/{selected_market}.")

# Footer
st.markdown("---")
st.markdown("CryptoGap+ | Advanced Crypto Arbitrage & Analysis Tool")
st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
