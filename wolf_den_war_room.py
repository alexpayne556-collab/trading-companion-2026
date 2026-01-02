#!/usr/bin/env python3
"""
🐺 WOLF DEN WAR ROOM - Bloomberg-Level Command Center

The only dashboard you need. Integrates everything.

Author: Brokkr
Date: January 2, 2026
"""

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from pathlib import Path
import json
import sys
import csv

# Page config
st.set_page_config(
    page_title="🐺 Wolf Den War Room",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add src to path for research modules
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from research.sector_rotation import SectorRotationTracker
    from research.catalyst_tracker import CatalystTracker
    from research.failed_breakout_detector import FailedBreakoutDetector
    RESEARCH_AVAILABLE = True
except:
    RESEARCH_AVAILABLE = False

# Header
st.title("🐺 WOLF DEN WAR ROOM")
st.caption(f"Command Center | {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}")

# Sidebar
st.sidebar.header("🎯 Mission Control")
mode = st.sidebar.radio(
    "Select Mission",
    ["📊 Overview", "🔥 Sectors", "📅 Catalysts", "💣 Breakouts", "🎯 Live Track"]
)

# Load watchlist
@st.cache_data(ttl=300)
def load_watchlist():
    try:
        with open('atp_watchlists/ATP_WOLF_PACK_MASTER.csv') as f:
            reader = csv.DictReader(f)
            return [row['Symbol'] for row in reader]
    except:
        return ['AISP', 'GOGO', 'LUNR', 'IONQ', 'SMR', 'RKLB']

tickers = load_watchlist()

#=== OVERVIEW ===
if mode == "📊 Overview":
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Account", "$1,280", "+2.1%")
    col2.metric("Cash", "$1,120", "87.5%")
    col3.metric("Positions", "1", "LUNR")
    col4.metric("Status", "HUNT MODE", "🐺")
    
    st.markdown("---")
    st.subheader("🎯 Top Conviction")
    
    try:
        with open('logs/conviction_rankings_latest.json') as f:
            rankings = json.load(f)
        df = pd.DataFrame(rankings).head(5)
        st.dataframe(df[['ticker', 'score', 'conviction', 'notes']], use_container_width=True)
    except:
        st.warning("Run: `python fast_conviction_scanner.py`")

#=== SECTORS ===
elif mode == "🔥 Sectors":
    if RESEARCH_AVAILABLE:
        tracker = SectorRotationTracker()
        with st.spinner("Analyzing sectors..."):
            df = tracker.get_sector_performance([5, 10, 20])
            ranked = tracker.rank_sectors(df)
            
        st.subheader("🚀 HOT SECTORS")
        for idx, row in ranked.head(5).iterrows():
            with st.expander(f"{'🔥' if row['5d'] > 5 else '🟢'} {row['sector']} - {row['5d']:+.1f}%"):
                col1, col2, col3 = st.columns(3)
                col1.metric("5d", f"{row['5d']:+.2f}%")
                col2.metric("10d", f"{row['10d']:+.2f}%")
                col3.metric("20d", f"{row['20d']:+.2f}%")
                
        alerts = tracker.generate_sector_alerts(ranked, threshold=3.0)
        if alerts:
            st.markdown("---")
            st.subheader("⚡ Alerts")
            for alert in alerts:
                if alert['alert_type'] == 'HOT_SECTOR':
                    st.success(f"🟢 {alert['sector']} +{alert['performance_5d']:.1f}%")
                    st.write(f"Tickers: {', '.join(alert['watchlist_tickers'])}")
    else:
        st.error("Research modules not loaded")

#=== CATALYSTS ===
elif mode == "📅 Catalysts":
    if RESEARCH_AVAILABLE:
        tracker = CatalystTracker()
        catalysts = tracker.get_all_catalysts(tickers, days_ahead=30)
        ranked = tracker.rank_catalysts(catalysts)
        
        if ranked:
            st.subheader(f"📅 {len(ranked)} Upcoming Catalysts")
            for cat in ranked:
                ticker = cat.get('ticker', 'MARKET')
                days = cat['days_until']
                urgency = "🔴" if days <= 3 else "🟡" if days <= 7 else "🟢"
                
                with st.expander(f"{urgency} {ticker} - {cat.get('event', 'Earnings')} ({days}d)"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Days", days)
                    col2.metric("Impact", cat['impact'])
                    col3.metric("Score", cat['score'])
        else:
            st.info("No catalysts in next 30 days")
    else:
        st.error("Research modules not loaded")

#=== BREAKOUTS ===
elif mode == "💣 Breakouts":
    if RESEARCH_AVAILABLE:
        detector = FailedBreakoutDetector()
        with st.spinner("Scanning breakouts..."):
            results = detector.scan_watchlist(tickers)
            
        if results:
            for result in results:
                result['score'] = detector.score_reversal_potential(result)
            results.sort(key=lambda x: x['score'], reverse=True)
            
            st.subheader(f"💣 {len(results)} Failed Breakouts")
            for fb in results:
                with st.expander(f"{fb['ticker']} - Score: {fb['score']}/100"):
                    col1, col2 = st.columns(2)
                    col1.metric("Run", f"+{fb['run_pct']:.1f}%")
                    col2.metric("Retrace", f"-{fb['retracement_pct']:.1f}%")
                    st.write(f"Peak: ${fb['high']:.2f} → Now: ${fb['current']:.2f}")
        else:
            st.info("No failed breakouts detected")
    else:
        st.error("Research modules not loaded")

#=== LIVE TRACK ===
elif mode == "🎯 Live Track":
    ticker = st.selectbox("Ticker", tickers, index=0)
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='5d')
        
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
        change = ((current - prev) / prev) * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Price", f"${current:.2f}", f"{change:+.1f}%")
        col2.metric("Volume", f"{hist['Volume'].iloc[-1]:,.0f}")
        
        year = stock.history(period='1y')
        low_52w = year['Low'].min()
        pct = ((current - low_52w) / low_52w) * 100
        col3.metric("From Low", f"+{pct:.1f}%")
        
        st.line_chart(hist['Close'])
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("---")
st.caption("🐺 Built by Brokkr | LLHR")
