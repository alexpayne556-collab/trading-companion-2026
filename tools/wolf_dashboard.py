#!/usr/bin/env python3
"""
🐺 WOLF PACK WAR ROOM - STREAMLIT DASHBOARD
============================================

The NUCLEAR CONTROL CENTER for preemptive strikes.

Run: streamlit run wolf_dashboard.py --server.port 8501

Features:
- Real-time whisper detection
- Catalyst calendar
- ML dip predictions
- Sector heat maps
- Position management
- The convergence view

AWOOOO! 🐺
"""

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page config
st.set_page_config(
    page_title="🐺 Wolf Pack War Room",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        text-shadow: 2px 2px 4px #000000;
    }
    .metric-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .whisper-hot {
        color: #FF6B6B;
        font-weight: bold;
    }
    .whisper-warm {
        color: #FFE66D;
    }
    .catalyst-imminent {
        background-color: #FF6B6B;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
    }
    .stMetric {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ===== DATA FUNCTIONS =====

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(ticker: str) -> dict:
    """Get stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period='1mo')
        
        price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        
        # Calculate metrics
        if len(hist) >= 5:
            week_return = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100
            month_return = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
            vol_ratio = hist['Volume'].iloc[-1] / hist['Volume'].mean() if hist['Volume'].mean() > 0 else 0
        else:
            week_return = month_return = vol_ratio = 0
        
        return {
            'ticker': ticker,
            'price': price,
            'week_return': week_return,
            'month_return': month_return,
            'volume_ratio': vol_ratio,
            'short_percent': info.get('shortPercentOfFloat', 0) or 0,
            'market_cap': info.get('marketCap', 0),
            'name': info.get('shortName', ticker),
        }
    except Exception as e:
        return {'ticker': ticker, 'price': 0, 'error': str(e)}


@st.cache_data(ttl=300)
def get_options_data(ticker: str) -> dict:
    """Get options data for whisper analysis"""
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options
        
        if not expirations:
            return {'signal': False}
        
        opt = stock.option_chain(expirations[0])
        calls = opt.calls
        puts = opt.puts
        
        call_oi = calls['openInterest'].sum()
        put_oi = puts['openInterest'].sum()
        call_vol = calls['volume'].sum()
        
        cp_ratio = call_oi / max(put_oi, 1)
        vol_oi = call_vol / max(call_oi, 1)
        
        # Max OI strike
        if len(calls) > 0:
            max_strike = calls.loc[calls['openInterest'].idxmax()]['strike']
        else:
            max_strike = 0
        
        return {
            'call_oi': call_oi,
            'put_oi': put_oi,
            'cp_ratio': cp_ratio,
            'vol_oi': vol_oi,
            'max_strike': max_strike,
            'expiration': expirations[0],
        }
    except:
        return {'signal': False}


def calculate_whisper_score(ticker: str) -> dict:
    """Calculate whisper score for a ticker"""
    stock_data = get_stock_data(ticker)
    options_data = get_options_data(ticker)
    
    score = 0
    signals = []
    
    # Options signals
    if options_data.get('cp_ratio', 0) > 2:
        score += 25
        signals.append(f"Call/Put: {options_data['cp_ratio']:.1f}x")
    
    if options_data.get('vol_oi', 0) > 0.5:
        score += 20
        signals.append(f"Vol/OI: {options_data['vol_oi']:.1f}")
    
    # Volume signal
    if stock_data.get('volume_ratio', 0) > 1.5:
        score += 25
        signals.append(f"Volume: {stock_data['volume_ratio']:.1f}x avg")
    
    # Short interest
    short_pct = stock_data.get('short_percent', 0)
    if short_pct > 0.15:
        score += 20
        signals.append(f"Short: {short_pct*100:.1f}%")
    
    return {
        'ticker': ticker,
        'name': stock_data.get('name', ticker),
        'price': stock_data.get('price', 0),
        'score': min(score, 100),
        'signals': signals,
        'week_return': stock_data.get('week_return', 0),
        'month_return': stock_data.get('month_return', 0),
        'short_percent': short_pct,
        'cp_ratio': options_data.get('cp_ratio', 0),
        'max_strike': options_data.get('max_strike', 0),
    }


# ===== WATCHLIST =====
WATCHLIST = {
    'Quantum/Photonics': ['QUBT', 'IONQ', 'QBTS', 'RGTI'],
    'Space': ['RDW', 'RKLB', 'LUNR', 'SPCE', 'MNTS'],
    'Nuclear': ['UUUU', 'SMR', 'OKLO', 'NNE', 'LEU'],
    'Rare Earth': ['USAR', 'MP'],
    'Photonics': ['LITE', 'AAOI', 'GFS', 'COHR'],
    'Drones': ['AVAV', 'JOBY'],
    'Positions': ['AISP'],
}

ALL_TICKERS = [t for tickers in WATCHLIST.values() for t in tickers]

# ===== CATALYSTS =====
CATALYSTS = {
    'RDW': {'date': '2026-01-07', 'event': 'CES Lunar Manufacturing Demo', 'time': '2:00 PM ET'},
    'QUBT': {'date': '2026-01-07', 'event': 'CES Photonics Presentation', 'time': '2:00 PM ET'},
    'IONQ': {'date': '2026-01-07', 'event': 'CES Quantum Demo', 'time': 'TBA'},
    'RKLB': {'date': '2026-01-10', 'event': 'Electron Launch Window', 'time': 'TBA'},
    'LUNR': {'date': '2026-01-15', 'event': 'IM-2 Mission Update', 'time': 'TBA'},
}

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("## 🐺 WOLF PACK")
    st.markdown("### War Room Controls")
    
    view = st.radio(
        "Select View",
        ["🎯 Command Center", "📡 Whisper Scanner", "📅 Catalyst Calendar", 
         "🔥 Sector Heat Map", "📊 Deep Dive", "💰 Positions"]
    )
    
    st.markdown("---")
    st.markdown("### Quick Stats")
    st.markdown(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
    st.markdown(f"**Time:** {datetime.now().strftime('%H:%M:%S')}")
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🐺 THE CREED")
    st.markdown("*We see the SETUP before the MOVE*")
    st.markdown("*We position EARLY*")
    st.markdown("*We let smart money do the lifting*")
    st.markdown("**AWOOOO!**")


# ===== MAIN VIEWS =====

if view == "🎯 Command Center":
    st.markdown("<h1 class='main-header'>🐺 WOLF PACK WAR ROOM</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #888;'>PREEMPTIVE STRIKE COMMAND CENTER</h3>", unsafe_allow_html=True)
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate top whisper
    with st.spinner("Scanning whispers..."):
        whisper_data = []
        for ticker in ['LUNR', 'QUBT', 'RDW', 'IONQ', 'UUUU']:
            data = calculate_whisper_score(ticker)
            whisper_data.append(data)
        
        whisper_data.sort(key=lambda x: x['score'], reverse=True)
        top_whisper = whisper_data[0]
    
    with col1:
        st.metric("🔥 Top Whisper", top_whisper['ticker'], f"Score: {top_whisper['score']}/100")
    
    with col2:
        # Next catalyst
        today = datetime.now().date()
        next_cat = None
        for ticker, cat in CATALYSTS.items():
            cat_date = datetime.strptime(cat['date'], '%Y-%m-%d').date()
            if cat_date >= today:
                if next_cat is None or cat_date < datetime.strptime(next_cat['date'], '%Y-%m-%d').date():
                    next_cat = {**cat, 'ticker': ticker}
        
        if next_cat:
            days_away = (datetime.strptime(next_cat['date'], '%Y-%m-%d').date() - today).days
            st.metric("📅 Next Catalyst", next_cat['ticker'], f"in {days_away} days")
    
    with col3:
        st.metric("📊 Watchlist", len(ALL_TICKERS), "tickers")
    
    with col4:
        st.metric("🎯 Sectors", len(WATCHLIST), "tracked")
    
    st.markdown("---")
    
    # Two column layout
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        st.markdown("### 🔥 TOP WHISPERS")
        
        whisper_df = pd.DataFrame(whisper_data)
        
        for _, row in whisper_df.iterrows():
            score = row['score']
            color = "🔥" if score >= 50 else "⚡" if score >= 25 else "○"
            
            with st.container():
                cols = st.columns([1, 2, 1, 2])
                cols[0].markdown(f"**{color} {row['ticker']}**")
                cols[1].markdown(f"${row['price']:.2f}")
                cols[2].markdown(f"Score: {score}")
                cols[3].markdown(f"{', '.join(row['signals'][:2]) if row['signals'] else 'No signals'}")
    
    with right_col:
        st.markdown("### 📅 THIS WEEK")
        
        for ticker, cat in CATALYSTS.items():
            cat_date = datetime.strptime(cat['date'], '%Y-%m-%d').date()
            days_away = (cat_date - today).days
            
            if 0 <= days_away <= 7:
                if days_away == 0:
                    badge = "🔴 TODAY"
                elif days_away == 1:
                    badge = "🟠 TOMORROW"
                else:
                    badge = f"🟢 {days_away} days"
                
                st.markdown(f"""
                **{ticker}** {badge}  
                {cat['event']}  
                *{cat['time']}*
                """)
                st.markdown("---")
    
    # Convergence section
    st.markdown("---")
    st.markdown("### 🎯 THE CONVERGENCE")
    st.markdown("*Where ALL signals align:*")
    
    conv_cols = st.columns(3)
    
    with conv_cols[0]:
        st.markdown("""
        **#1 LUNR**
        - Whisper: 70/85 🔥
        - ML Dip: 98% probability
        - Short: 22%
        - Smart money accumulating
        """)
    
    with conv_cols[1]:
        st.markdown("""
        **#2 QUBT**  
        - CES: TOMORROW 2 PM
        - Photonics + Quantum
        - Short: 22.7%
        - $12 entry point
        """)
    
    with conv_cols[2]:
        st.markdown("""
        **#3 RDW**
        - CES: TOMORROW 2 PM
        - Options flow active
        - Space laggard
        - 60 Minutes exposure
        """)


elif view == "📡 Whisper Scanner":
    st.markdown("## 📡 WHISPER SCANNER")
    st.markdown("*Detecting setups BEFORE the move*")
    
    # Scan controls
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔍 Full Scan", type="primary"):
            st.session_state['run_scan'] = True
    
    # Run scan
    with st.spinner("Scanning for whispers..."):
        all_whispers = []
        progress = st.progress(0)
        
        for i, ticker in enumerate(ALL_TICKERS):
            data = calculate_whisper_score(ticker)
            all_whispers.append(data)
            progress.progress((i + 1) / len(ALL_TICKERS))
        
        all_whispers.sort(key=lambda x: x['score'], reverse=True)
    
    # Results
    st.markdown("### 🔥 WHISPER RESULTS")
    
    # Hot whispers
    hot = [w for w in all_whispers if w['score'] >= 40]
    warm = [w for w in all_whispers if 20 <= w['score'] < 40]
    cold = [w for w in all_whispers if w['score'] < 20]
    
    tab1, tab2, tab3 = st.tabs([f"🔥 Hot ({len(hot)})", f"⚡ Warm ({len(warm)})", f"○ Cold ({len(cold)})"])
    
    with tab1:
        if hot:
            df = pd.DataFrame(hot)
            st.dataframe(
                df[['ticker', 'name', 'price', 'score', 'week_return', 'short_percent', 'cp_ratio']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hot whispers detected")
    
    with tab2:
        if warm:
            df = pd.DataFrame(warm)
            st.dataframe(
                df[['ticker', 'name', 'price', 'score', 'week_return']],
                use_container_width=True,
                hide_index=True
            )
    
    with tab3:
        if cold:
            df = pd.DataFrame(cold)
            st.dataframe(
                df[['ticker', 'name', 'price', 'score']],
                use_container_width=True,
                hide_index=True
            )
    
    # Whisper explanation
    with st.expander("ℹ️ How Whisper Scoring Works"):
        st.markdown("""
        **Whisper Score** detects SETUP signals before the move:
        
        | Signal | Points | What It Means |
        |--------|--------|---------------|
        | Call/Put > 2x | +25 | Bullish options positioning |
        | Vol/OI > 0.5 | +20 | New positions being opened |
        | Volume > 1.5x | +25 | Accumulation happening |
        | Short > 15% | +20 | Squeeze fuel |
        
        **Score 50+** = Something is being SET UP 🔥  
        **Score 25-49** = Watch closely ⚡  
        **Score <25** = No clear setup ○
        """)


elif view == "📅 Catalyst Calendar":
    st.markdown("## 📅 CATALYST CALENDAR")
    st.markdown("*Know WHEN events happen*")
    
    today = datetime.now().date()
    
    # This week view
    st.markdown("### 📆 This Week")
    
    # Create calendar-like view
    week_start = today - timedelta(days=today.weekday())
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    cols = st.columns(7)
    
    for i, col in enumerate(cols):
        day = week_start + timedelta(days=i)
        is_today = day == today
        
        with col:
            if is_today:
                st.markdown(f"**🔴 {days[i]}**")
                st.markdown(f"**{day.strftime('%m/%d')}**")
            else:
                st.markdown(f"**{days[i]}**")
                st.markdown(f"{day.strftime('%m/%d')}")
            
            # Check for catalysts on this day
            for ticker, cat in CATALYSTS.items():
                cat_date = datetime.strptime(cat['date'], '%Y-%m-%d').date()
                if cat_date == day:
                    st.markdown(f"🎯 **{ticker}**")
                    st.caption(cat['event'][:20] + "...")
    
    st.markdown("---")
    
    # Full catalyst list
    st.markdown("### 📋 All Upcoming Catalysts")
    
    catalyst_list = []
    for ticker, cat in CATALYSTS.items():
        cat_date = datetime.strptime(cat['date'], '%Y-%m-%d').date()
        days_away = (cat_date - today).days
        
        if days_away >= 0:
            catalyst_list.append({
                'Ticker': ticker,
                'Event': cat['event'],
                'Date': cat['date'],
                'Time': cat['time'],
                'Days Away': days_away
            })
    
    catalyst_list.sort(key=lambda x: x['Days Away'])
    
    df = pd.DataFrame(catalyst_list)
    st.dataframe(df, use_container_width=True, hide_index=True)


elif view == "🔥 Sector Heat Map":
    st.markdown("## 🔥 SECTOR HEAT MAP")
    st.markdown("*Find laggards in hot sectors*")
    
    # Calculate sector performance
    sector_data = []
    
    with st.spinner("Analyzing sectors..."):
        for sector, tickers in WATCHLIST.items():
            sector_returns = []
            for ticker in tickers:
                data = get_stock_data(ticker)
                if data.get('week_return'):
                    sector_returns.append(data['week_return'])
            
            if sector_returns:
                avg_return = sum(sector_returns) / len(sector_returns)
                sector_data.append({
                    'Sector': sector,
                    'Avg Return': avg_return,
                    'Tickers': len(tickers),
                    'Best': max(sector_returns),
                    'Worst': min(sector_returns)
                })
    
    # Sort by performance
    sector_data.sort(key=lambda x: x['Avg Return'], reverse=True)
    
    # Heat map visualization
    df = pd.DataFrame(sector_data)
    
    fig = px.bar(
        df,
        x='Sector',
        y='Avg Return',
        color='Avg Return',
        color_continuous_scale=['red', 'yellow', 'green'],
        title='Sector Performance (1 Week)'
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Laggard finder
    st.markdown("### 🎯 LAGGARDS IN HOT SECTORS")
    st.markdown("*Stocks that haven't run while their sector is hot*")
    
    laggards = []
    for sector, tickers in WATCHLIST.items():
        sector_avg = next((s['Avg Return'] for s in sector_data if s['Sector'] == sector), 0)
        
        for ticker in tickers:
            data = get_stock_data(ticker)
            if data.get('week_return', 0) < sector_avg - 5:  # Lagging by 5%+
                laggards.append({
                    'Ticker': ticker,
                    'Sector': sector,
                    'Return': data.get('week_return', 0),
                    'Sector Avg': sector_avg,
                    'Gap': data.get('week_return', 0) - sector_avg
                })
    
    if laggards:
        laggards.sort(key=lambda x: x['Gap'])
        df = pd.DataFrame(laggards)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No significant laggards found")


elif view == "📊 Deep Dive":
    st.markdown("## 📊 DEEP DIVE")
    
    # Ticker selector
    ticker = st.selectbox("Select Ticker", ALL_TICKERS, index=ALL_TICKERS.index('LUNR') if 'LUNR' in ALL_TICKERS else 0)
    
    if ticker:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Price chart
            stock = yf.Ticker(ticker)
            hist = stock.history(period='3mo')
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name=ticker
            ))
            fig.update_layout(
                title=f'{ticker} - 3 Month Chart',
                yaxis_title='Price',
                xaxis_title='Date',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Whisper analysis
            whisper = calculate_whisper_score(ticker)
            
            st.markdown(f"### {whisper['name']}")
            st.metric("Price", f"${whisper['price']:.2f}")
            st.metric("Whisper Score", f"{whisper['score']}/100")
            
            st.markdown("**Signals:**")
            for signal in whisper['signals']:
                st.markdown(f"✓ {signal}")
            
            if not whisper['signals']:
                st.markdown("○ No signals detected")
            
            # Options data
            st.markdown("---")
            st.markdown("**Options:**")
            st.markdown(f"Call/Put Ratio: {whisper['cp_ratio']:.1f}x")
            st.markdown(f"Max OI Strike: ${whisper['max_strike']:.2f}")
            
            # Catalyst check
            if ticker in CATALYSTS:
                st.markdown("---")
                st.markdown("**🎯 Catalyst:**")
                cat = CATALYSTS[ticker]
                st.markdown(f"{cat['event']}")
                st.markdown(f"Date: {cat['date']}")
                st.markdown(f"Time: {cat['time']}")


elif view == "💰 Positions":
    st.markdown("## 💰 CURRENT POSITIONS")
    
    # Manual position input (would connect to real data)
    positions = [
        {'Ticker': 'USAR', 'Shares': 5, 'Avg Cost': 15.80, 'Account': 'Robinhood'},
        {'Ticker': 'UUUU', 'Shares': 5, 'Avg Cost': 18.47, 'Account': 'Robinhood'},
        {'Ticker': 'AISP', 'Shares': 89, 'Avg Cost': 3.27, 'Account': 'Robinhood'},
    ]
    
    # Get current prices
    for pos in positions:
        data = get_stock_data(pos['Ticker'])
        pos['Current'] = data.get('price', 0)
        pos['Value'] = pos['Shares'] * pos['Current']
        pos['Cost Basis'] = pos['Shares'] * pos['Avg Cost']
        pos['P/L'] = pos['Value'] - pos['Cost Basis']
        pos['P/L %'] = ((pos['Current'] - pos['Avg Cost']) / pos['Avg Cost'] * 100) if pos['Avg Cost'] > 0 else 0
    
    # Summary metrics
    total_value = sum(p['Value'] for p in positions)
    total_cost = sum(p['Cost Basis'] for p in positions)
    total_pl = total_value - total_cost
    total_pl_pct = (total_pl / total_cost * 100) if total_cost > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Value", f"${total_value:.2f}")
    col2.metric("Cost Basis", f"${total_cost:.2f}")
    col3.metric("P/L", f"${total_pl:.2f}", f"{total_pl_pct:+.1f}%")
    col4.metric("Cash (RH)", "$363", "+$500 Fidelity")
    
    st.markdown("---")
    
    # Positions table
    df = pd.DataFrame(positions)
    st.dataframe(
        df[['Ticker', 'Shares', 'Avg Cost', 'Current', 'Value', 'P/L', 'P/L %', 'Account']],
        use_container_width=True,
        hide_index=True
    )
    
    # Position breakdown chart
    fig = px.pie(
        df,
        values='Value',
        names='Ticker',
        title='Portfolio Allocation'
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    st.plotly_chart(fig, use_container_width=True)


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🐺 WOLF PACK WAR ROOM | Built by Tyr, Fenrir & Brokkr | AWOOOO! 🐺
</div>
""", unsafe_allow_html=True)
