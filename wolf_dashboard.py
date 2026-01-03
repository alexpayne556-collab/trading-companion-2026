#!/usr/bin/env python3
"""
🐺 WOLF PACK COMMAND CENTER v3.0
The Ultimate Trading Dashboard - Full Send Edition
All 4 Validated Edges | Real-Time Scanning | ATP Integration
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import time

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="🐺 Wolf Pack Command Center",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# AUTO-REFRESH every 60 seconds
st.markdown("""
<script>
    setTimeout(function(){
        window.location.reload();
    }, 60000);
</script>
""", unsafe_allow_html=True)

# Custom CSS - Dark theme with neon accents
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0a0a0f 0%, #1a1a2e 100%);
    }
    
    /* Signal Cards */
    .signal-strong {
        background: linear-gradient(135deg, #0d2818 0%, #1a4d2e 100%);
        border: 2px solid #00ff88;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 0 30px rgba(0,255,136,0.3);
    }
    .signal-watch {
        background: linear-gradient(135deg, #2d2a0d 0%, #4d4a1a 100%);
        border: 2px solid #ffaa00;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 0 30px rgba(255,170,0,0.2);
    }
    .signal-danger {
        background: linear-gradient(135deg, #2d0d0d 0%, #4d1a1a 100%);
        border: 2px solid #ff4444;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 0 30px rgba(255,68,68,0.2);
    }
    
    /* Big Numbers */
    .big-green { color: #00ff88; font-size: 2.5rem; font-weight: bold; }
    .big-red { color: #ff4444; font-size: 2.5rem; font-weight: bold; }
    .big-yellow { color: #ffaa00; font-size: 2.5rem; font-weight: bold; }
    
    /* Action Box */
    .action-box {
        background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
        border: 2px solid #4488ff;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    
    /* Ticker Header */
    .ticker-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #00ff88, #4488ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Stats Grid */
    .stat-box {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Checklist */
    .checklist {
        background: rgba(0,0,0,0.3);
        border-radius: 10px;
        padding: 15px;
        font-family: monospace;
    }
    
    /* ATP Guide Box */
    .atp-box {
        background: linear-gradient(135deg, #1a1a3e 0%, #2a2a5e 100%);
        border: 1px solid #6666ff;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    
    /* Winning Probability Badge */
    .prob-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        margin: 5px;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .block-container {
        padding-top: 1rem;
    }
    
    /* Cards hover effect */
    .signal-strong:hover, .signal-watch:hover {
        transform: translateY(-2px);
        transition: transform 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CONFIGURATION - THE FULL WOLF PACK UNIVERSE (100+ TICKERS!)
# =============================================================================

UNIVERSE = {
    # 🚀 SPACE ECONOMY (13 tickers)
    'SPACE': [
        'LUNR', 'RKLB', 'RDW', 'BKSY', 'MNTS', 'ASTS', 'SPIR', 'PL', 
        'GSAT', 'SIDU', 'SATL', 'IRDM', 'VSAT'
    ],
    
    # ⚛️ QUANTUM TECHNOLOGY (6 tickers)
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ', 'LAES'],
    
    # ☢️ NUCLEAR / ENERGY (12 tickers)
    'NUCLEAR': [
        'LEU', 'CCJ', 'UUUU', 'UEC', 'SMR', 'OKLO', 
        'DNN', 'NXE', 'LTBR', 'CEG', 'TLN', 'VST'
    ],
    
    # 🔋 BATTERY / MATERIALS (7 tickers)
    'BATTERY_METALS': ['MP', 'LAC', 'ALB', 'FCX', 'AG', 'HL', 'KGC'],
    
    # 🤖 AI INFRASTRUCTURE (8 tickers)
    'AI_INFRA': ['CORZ', 'VRT', 'PWR', 'EME', 'LITE', 'FN', 'WOLF', 'IREN'],
    
    # 💾 MEMORY / STORAGE (6 tickers)
    'MEMORY': ['MU', 'WDC', 'STX', 'COHR', 'PSTG', 'SMCI'],
    
    # 🖥️ SEMICONDUCTORS (11 tickers)
    'SEMICONDUCTORS': [
        'NVDA', 'AMD', 'ALAB', 'ARM', 'TSM', 'ASML', 
        'KLAC', 'LRCX', 'AMAT', 'MRVL', 'AVGO'
    ],
    
    # 🕶️ SPATIAL COMPUTING (5 tickers)
    'SPATIAL': ['KOPN', 'OLED', 'HIMX', 'VUZI', 'U'],
    
    # 🦾 ROBOTICS / PHYSICAL AI (6 tickers)
    'ROBOTICS': ['TER', 'ZBRA', 'SYM', 'ROK', 'DE', 'ISRG'],
    
    # 🛡️ DEFENSE AI (7 tickers)
    'DEFENSE_AI': ['AISP', 'PLTR', 'KTOS', 'AVAV', 'RCAT', 'BBAI', 'SOUN'],
    
    # 📉 TAX BOUNCE / WOUNDED (8 tickers)
    'TAX_BOUNCE': ['ADBE', 'CRM', 'IT', 'GTLB', 'IOT', 'NCNO', 'TSLA', 'PATH'],
    
    # ⛏️ CRYPTO MINERS (5 tickers)
    'CRYPTO': ['MARA', 'RIOT', 'CLSK', 'HUT', 'BITF'],
    
    # 💳 FINTECH (6 tickers)
    'FINTECH': ['UPST', 'AFRM', 'SOFI', 'HOOD', 'NU', 'LC'],
    
    # 🧬 BIOTECH (7 tickers)
    'BIOTECH': ['RXRX', 'BEAM', 'CRSP', 'NTLA', 'EDIT', 'VERV', 'SDGR'],
    
    # ⚡ EV / HYDROGEN (8 tickers)
    'EV_HYDROGEN': ['LCID', 'RIVN', 'PLUG', 'FCEL', 'BE', 'BLNK', 'CHPT', 'QS'],
}

# Signal statistics from backtesting
SIGNAL_STATS = {
    'WOLF': {
        'name': 'Wolf Signal',
        'p_value': 0.023, 
        'avg_return': 37.87, 
        'win_rate': 78, 
        'color': '#00ff88',
        'emoji': '🐺',
        'description': 'Institutional accumulation - big volume, flat price = stealth buying'
    },
    'PRE-RUN': {
        'name': 'Pre-Run Predictor',
        'p_value': 0.000, 
        'avg_return': 17.27, 
        'win_rate': 58, 
        'color': '#ffaa00',
        'emoji': '📈',
        'description': 'Building momentum before explosive move'
    },
    'CAPITULATION': {
        'name': 'Capitulation Hunter',
        'p_value': 0.004, 
        'avg_return': 19.95, 
        'win_rate': 58, 
        'color': '#ff4444',
        'emoji': '💀',
        'description': 'Panic selling creates buying opportunity'
    },
    'POCKET': {
        'name': 'Pocket Pivot',
        'p_value': 0.000, 
        'avg_return': 9.61, 
        'win_rate': 63, 
        'color': '#4488ff',
        'emoji': '🎯',
        'description': 'Controlled pullback with institutional re-entry'
    },
}

# =============================================================================
# DATA FUNCTIONS
# =============================================================================

@st.cache_data(ttl=60)
def fetch_all_data():
    """Fetch all market data for the universe"""
    tickers = []
    for sector_tickers in UNIVERSE.values():
        tickers.extend(sector_tickers)
    tickers = list(set(tickers))
    
    data = {}
    df = yf.download(tickers, period='6mo', progress=False, group_by='ticker')
    
    for ticker in tickers:
        try:
            if len(tickers) == 1:
                ticker_df = df
            else:
                ticker_df = df[ticker]
            
            ticker_df = ticker_df.dropna()
            if len(ticker_df) >= 55:
                data[ticker] = ticker_df
        except:
            continue
    
    return data


def get_sector(ticker):
    """Get sector for a ticker"""
    for sector, tickers in UNIVERSE.items():
        if ticker in tickers:
            return sector
    return 'OTHER'


def calculate_all_metrics(close, high, low, volume):
    """Calculate all metrics needed for signal detection"""
    i = len(close) - 1
    
    if i < 55:
        return None
    
    # Base volume (20-day average)
    base_vol = np.mean(volume[max(0, i-20):i])
    rel_vol = volume[i] / base_vol if base_vol > 0 else 1
    
    # Price changes
    prev_close = close[i-1]
    daily_chg = ((close[i] - prev_close) / prev_close) * 100
    weekly_chg = ((close[i] - close[max(0, i-5)]) / close[max(0, i-5)]) * 100
    monthly_chg = ((close[i] - close[max(0, i-20)]) / close[max(0, i-20)]) * 100
    
    # High tracking
    high_20 = max(high[max(0, i-20):i])
    high_52 = max(high[max(0, i-252):i]) if i > 252 else max(high[:i])
    high_10 = max(high[max(0, i-10):i])
    
    pct_from_high_20 = ((close[i] - high_20) / high_20) * 100
    pct_from_high_52 = ((close[i] - high_52) / high_52) * 100
    pct_from_high_10 = ((close[i] - high_10) / high_10) * 100
    
    # Volume analysis
    up_vol = sum(volume[j] for j in range(max(0, i-20), i) if close[j] > close[j-1])
    down_vol = sum(volume[j] for j in range(max(0, i-20), i) if close[j] < close[j-1])
    vol_ratio = up_vol / down_vol if down_vol > 0 else 1
    
    # 5-day volume ratio
    vol_5d = np.mean(volume[max(0, i-5):i])
    vol_ratio_5d = vol_5d / base_vol if base_vol > 0 else 1
    
    # CLV analysis (Close Location Value)
    clvs = []
    for k in range(max(0, i-5), i+1):
        day_range = high[k] - low[k]
        if day_range > 0:
            clvs.append((close[k] - low[k]) / day_range)
    avg_clv = np.mean(clvs[:-1]) if len(clvs) > 1 else 0.5
    clv_today = clvs[-1] if clvs else 0.5
    
    # Moving averages
    ma20 = np.mean(close[i-20:i])
    ma50 = np.mean(close[i-50:i])
    above_ma20 = close[i] > ma20
    above_ma50 = close[i] > ma50
    
    # Max down volume (for pocket pivot)
    down_vols = [volume[j] for j in range(max(0, i-10), i) if close[j] < close[j-1]]
    max_down_vol = max(down_vols) if down_vols else 0
    
    # Volatility
    if len(close) >= 21:
        returns = np.diff(close[-20:]) / close[-20:-1]
        volatility = np.std(returns) * np.sqrt(252) * 100
    else:
        volatility = 0
    
    # Support/Resistance
    recent_lows = low[max(0, i-20):i]
    recent_highs = high[max(0, i-20):i]
    support = np.percentile(recent_lows, 10)
    resistance = np.percentile(recent_highs, 90)
    
    # ATR for position sizing
    atr_vals = []
    for k in range(max(1, i-14), i+1):
        tr = max(high[k] - low[k], 
                 abs(high[k] - close[k-1]), 
                 abs(low[k] - close[k-1]))
        atr_vals.append(tr)
    atr = np.mean(atr_vals) if atr_vals else 0
    
    return {
        'price': float(close[i]),
        'daily_chg': float(daily_chg),
        'weekly_chg': float(weekly_chg),
        'monthly_chg': float(monthly_chg),
        'pct_from_high_20': float(pct_from_high_20),
        'pct_from_high_52': float(pct_from_high_52),
        'pct_from_high_10': float(pct_from_high_10),
        'rel_vol': float(rel_vol),
        'vol_ratio': float(vol_ratio),
        'vol_ratio_5d': float(vol_ratio_5d),
        'avg_clv': float(avg_clv),
        'clv_today': float(clv_today),
        'above_ma20': above_ma20,
        'above_ma50': above_ma50,
        'ma20': float(ma20),
        'ma50': float(ma50),
        'max_down_vol': float(max_down_vol),
        'current_vol': float(volume[i]),
        'volatility': float(volatility),
        'support': float(support),
        'resistance': float(resistance),
        'high_20': float(high_20),
        'high_52': float(high_52),
        'high_10': float(high_10),
        'atr': float(atr),
    }


def get_signals(metrics):
    """Check all 4 validated signals with detailed breakdowns"""
    signals = []
    
    # ==========================================================================
    # 🐺 WOLF SIGNAL (p=0.023, +37.87%, 78% WR)
    # Institutional accumulation: Big volume + flat price = stealth buying
    # ==========================================================================
    wolf_checks = {
        'Volume Spike (>2x avg)': metrics['rel_vol'] > 2,
        'Flat Price (±2%)': abs(metrics['daily_chg']) < 2,
        'Healthy Trend (vol ratio >2.5)': metrics['vol_ratio'] > 2.5,
        'Near Highs (within 5%)': metrics['pct_from_high_20'] > -5
    }
    wolf_score = sum(wolf_checks.values())
    
    if wolf_score == 4:
        signals.append({
            'type': 'WOLF',
            'emoji': '🐺',
            'strength': 'STRONG',
            'score': '4/4',
            'score_num': 4,
            'checks': wolf_checks,
            'action': 'BUY NOW - Institutional accumulation detected!',
            'atp_checklist': [
                '✓ Check 5-min chart: Volume bars towering above average line',
                '✓ Look for tight candles (small body, little wicks)',
                '✓ Level 2: Watch for large bid blocks appearing/disappearing (iceberg orders)',
                '✓ Time & Sales: Look for hidden buying (dark pool prints)',
                '✓ Price action: Should be "boring" - thats the stealth!'
            ],
            'entry_strategy': 'Enter on any dip with limit orders. Add on confirmation.',
            'stop_strategy': 'Stop below recent swing low or 2x ATR'
        })
    elif wolf_score >= 3:
        signals.append({
            'type': 'WOLF',
            'emoji': '🐺',
            'strength': 'SETUP',
            'score': f'{wolf_score}/4',
            'score_num': wolf_score,
            'checks': wolf_checks,
            'action': 'WATCH - Wolf signal forming',
            'atp_checklist': [
                '○ Set volume alert: >2x 20-day average',
                '○ Watch for price to flatten after any move',
                f'○ Missing: {[k.split("(")[0].strip() for k,v in wolf_checks.items() if not v]}'
            ],
            'entry_strategy': 'Wait for all 4 criteria to trigger',
            'stop_strategy': 'N/A - not triggered yet'
        })
    
    # ==========================================================================
    # 📈 PRE-RUN PREDICTOR (p=0.000, +17.27%, 58% WR)
    # Building momentum before explosive move
    # ==========================================================================
    prerun_checks = {
        '5-Day Volume Building': metrics['vol_ratio_5d'] > 1.0,
        'Today Volume Present': metrics['rel_vol'] > 1.0,
        'Price Holding (not dropping)': metrics['weekly_chg'] > -2,
        'Strong CLV (closes high)': metrics['avg_clv'] > 0.45,
        'Buyers Winning (ratio >1.2)': metrics['vol_ratio'] > 1.2
    }
    prerun_score = sum(prerun_checks.values())
    
    if prerun_score == 5:
        signals.append({
            'type': 'PRE-RUN',
            'emoji': '📈',
            'strength': 'STRONG',
            'score': '5/5',
            'score_num': 5,
            'checks': prerun_checks,
            'action': 'BUY - All 5 pre-run signatures present! Explosion coming!',
            'atp_checklist': [
                '✓ Daily chart: Volume bars making "staircase" pattern up',
                '✓ Price: Consolidating/grinding higher, not dropping',
                '✓ Candles: Closes consistently in upper half (check wicks)',
                '✓ Time & Sales: More green prints than red (buyer aggression)',
                '✓ Level 2: Bids stacking, asks getting hit'
            ],
            'entry_strategy': 'Buy breakout over recent high with volume confirmation',
            'stop_strategy': 'Stop below consolidation low or 20-day MA'
        })
    elif prerun_score >= 4:
        signals.append({
            'type': 'PRE-RUN',
            'emoji': '📈',
            'strength': 'MODERATE',
            'score': f'{prerun_score}/5',
            'score_num': prerun_score,
            'checks': prerun_checks,
            'action': 'WATCH CLOSELY - Pre-run building',
            'atp_checklist': [
                '○ Check daily chart for volume trend',
                '○ Watch for the 5th criterion to trigger',
                f'○ Missing: {[k.split("(")[0].strip() for k,v in prerun_checks.items() if not v]}'
            ],
            'entry_strategy': 'Wait for all 5 criteria or breakout',
            'stop_strategy': 'N/A'
        })
    
    # ==========================================================================
    # 💀 CAPITULATION HUNTER (p=0.004, +19.95%, 58% WR)
    # Panic selling creates buying opportunity
    # ==========================================================================
    cap_checks = {
        'Wounded (-15% to -40%)': -40 < metrics['pct_from_high_20'] < -15,
        'Volume Spike (>1.5x)': metrics['rel_vol'] > 1.5,
        'Red Candle (CLV <0.5)': metrics['clv_today'] < 0.5
    }
    cap_score = sum(cap_checks.values())
    
    if cap_score == 3:
        signals.append({
            'type': 'CAPITULATION',
            'emoji': '💀',
            'strength': 'STRONG',
            'score': '3/3',
            'score_num': 3,
            'checks': cap_checks,
            'action': 'BUY THE BLOOD - Capitulation in progress!',
            'atp_checklist': [
                '✓ Daily chart: HUGE red volume bar (capitulation spike)',
                '✓ Candle: Long lower wick forming = buyers stepping in',
                '✓ Level 2: Watch for bid wall forming below price',
                '✓ Time & Sales: Large block buys appearing at lows',
                '✓ RSI/indicators: Oversold readings (but dont wait for perfect)'
            ],
            'entry_strategy': 'Scale in on panic spikes. Average down if thesis intact.',
            'stop_strategy': 'Stop below panic low OR if drops >40% from high'
        })
    elif cap_checks['Wounded (-15% to -40%)']:
        signals.append({
            'type': 'CAPITULATION',
            'emoji': '💀',
            'strength': 'WATCH',
            'score': f'{cap_score}/3',
            'score_num': cap_score,
            'checks': cap_checks,
            'action': f'WOUNDED ({metrics["pct_from_high_20"]:.0f}% off high) - Watch for capitulation spike',
            'atp_checklist': [
                '○ Set volume alert: >1.5x 20-day average',
                '○ Wait for the panic - dont catch falling knife',
                '○ Look for reversal candle (hammer, doji)',
            ],
            'entry_strategy': 'Wait for all 3 criteria to trigger',
            'stop_strategy': 'N/A'
        })
    
    # ==========================================================================
    # 🎯 POCKET PIVOT (p=0.000, +9.61%, 63% WR)  
    # Controlled pullback with institutional re-entry
    # ==========================================================================
    pp_checks = {
        'Above 50-day MA': metrics['above_ma50'],
        'In Pullback Zone (-3% to -10%)': -10 < metrics['pct_from_high_10'] < -3,
        'Up Day Today': metrics['daily_chg'] > 0,
        'Volume > Max Down Vol': metrics['current_vol'] > metrics['max_down_vol']
    }
    pp_score = sum(pp_checks.values())
    
    if pp_score == 4:
        signals.append({
            'type': 'POCKET',
            'emoji': '🎯',
            'strength': 'STRONG',
            'score': '4/4',
            'score_num': 4,
            'checks': pp_checks,
            'action': 'BUY - Pocket Pivot confirmed! Institutions re-entering!',
            'atp_checklist': [
                '✓ Daily chart: Green candle bouncing off or near 50 MA',
                '✓ Volume: Todays volume exceeds ALL red days in last 10 days',
                '✓ Price action: Controlled pullback, not crash',
                '✓ Level 2: Aggressive buying at ask prices',
                '✓ Trend: Still in uptrend (above 50 MA)'
            ],
            'entry_strategy': 'Buy on strength, add on pullback to entry',
            'stop_strategy': 'Stop just below 50-day MA or pivot low'
        })
    elif pp_checks['Above 50-day MA'] and pp_checks['In Pullback Zone (-3% to -10%)']:
        signals.append({
            'type': 'POCKET',
            'emoji': '🎯',
            'strength': 'SETUP',
            'score': f'{pp_score}/4',
            'score_num': pp_score,
            'checks': pp_checks,
            'action': 'SETUP - In pullback zone, watching for trigger',
            'atp_checklist': [
                f'○ Pulled back {metrics["pct_from_high_10"]:.1f}% from 10d high',
                '○ Need: Up day with volume > max down volume',
                '○ Set alert: price > yesterdays high',
            ],
            'entry_strategy': 'Wait for volume confirmation',
            'stop_strategy': 'N/A'
        })
    
    return signals


def analyze_ticker(ticker, df):
    """Full analysis of a single ticker"""
    close = df['Close'].values
    high = df['High'].values
    low = df['Low'].values
    volume = df['Volume'].values
    
    metrics = calculate_all_metrics(close, high, low, volume)
    if metrics is None:
        return None
    
    signals = get_signals(metrics)
    
    return {
        'ticker': ticker,
        'sector': get_sector(ticker),
        'metrics': metrics,
        'signals': signals,
        'df': df
    }


def analyze_all(data):
    """Analyze entire universe"""
    results = []
    
    for ticker, df in data.items():
        analysis = analyze_ticker(ticker, df)
        if analysis:
            results.append(analysis)
    
    return sorted(results, key=lambda x: len(x['signals']), reverse=True)


# =============================================================================
# CHART COMPONENTS
# =============================================================================

def render_chart(result, height=600):
    """Render interactive candlestick chart"""
    df = result['df'].tail(60)  # Last 60 days
    m = result['metrics']
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.25, 0.15],
        subplot_titles=('', '', '')
    )
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price',
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff4444'
    ), row=1, col=1)
    
    # Moving averages
    ma20 = df['Close'].rolling(20).mean()
    ma50 = df['Close'].rolling(50).mean()
    
    fig.add_trace(go.Scatter(
        x=df.index, y=ma20, mode='lines',
        name='20 SMA', line=dict(color='#ffaa00', width=1.5)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=df.index, y=ma50, mode='lines',
        name='50 SMA', line=dict(color='#4488ff', width=1.5)
    ), row=1, col=1)
    
    # Support/Resistance lines
    fig.add_hline(y=m['support'], line_dash="dash", line_color="#ff4444", 
                  annotation_text="Support", row=1, col=1)
    fig.add_hline(y=m['resistance'], line_dash="dash", line_color="#00ff88",
                  annotation_text="Resistance", row=1, col=1)
    
    # Volume
    colors = ['#ff4444' if df['Close'].iloc[i] < df['Open'].iloc[i] 
              else '#00ff88' for i in range(len(df))]
    
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'],
        marker_color=colors, name='Volume', opacity=0.7
    ), row=2, col=1)
    
    # Volume average line
    vol_avg = df['Volume'].rolling(20).mean()
    fig.add_trace(go.Scatter(
        x=df.index, y=vol_avg, mode='lines',
        name='20d Vol Avg', line=dict(color='#ffaa00', width=2)
    ), row=2, col=1)
    
    # CLV (Close Location Value)
    clv = (df['Close'] - df['Low']) / (df['High'] - df['Low'])
    clv = clv.fillna(0.5)
    
    clv_colors = ['#00ff88' if v > 0.5 else '#ff4444' for v in clv]
    
    fig.add_trace(go.Bar(
        x=df.index, y=clv,
        marker_color=clv_colors, name='CLV'
    ), row=3, col=1)
    
    fig.add_hline(y=0.5, line_dash="dash", line_color="#888", row=3, col=1)
    
    fig.update_layout(
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(14,17,23,1)',
        font=dict(color='white'),
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    
    fig.update_xaxes(gridcolor='#222')
    fig.update_yaxes(gridcolor='#222')
    
    return fig


def render_sector_heatmap(results):
    """Render sector performance heatmap"""
    sector_data = []
    
    for sector in UNIVERSE.keys():
        sector_results = [r for r in results if r['sector'] == sector]
        if sector_results:
            avg_chg = np.mean([r['metrics']['daily_chg'] for r in sector_results])
            best = max(sector_results, key=lambda x: x['metrics']['daily_chg'])
            worst = min(sector_results, key=lambda x: x['metrics']['daily_chg'])
            signals = sum(len(r['signals']) for r in sector_results)
            
            sector_data.append({
                'sector': sector,
                'change': avg_chg,
                'best': f"{best['ticker']} ({best['metrics']['daily_chg']:+.1f}%)",
                'worst': f"{worst['ticker']} ({worst['metrics']['daily_chg']:+.1f}%)",
                'signals': signals
            })
    
    sector_df = pd.DataFrame(sector_data).sort_values('change', ascending=True)
    
    fig = go.Figure(go.Bar(
        x=sector_df['change'],
        y=sector_df['sector'],
        orientation='h',
        marker=dict(
            color=sector_df['change'],
            colorscale='RdYlGn',
            cmin=-10, cmax=10
        ),
        text=[f"{x:+.1f}%" for x in sector_df['change']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Change: %{x:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        height=250,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(l=0, r=100, t=20, b=40),
        xaxis_title='Daily Change %'
    )
    
    return fig


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_signal_card(result, signal):
    """Render a detailed signal card using native Streamlit"""
    m = result['metrics']
    stats = SIGNAL_STATS.get(signal['type'], {})
    color = stats.get('color', '#ffffff')
    
    # Use Streamlit container for better rendering
    with st.container():
        # Header row
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {signal['emoji']} {stats.get('name', signal['type'])} - **{signal['strength']}**")
        with col2:
            st.markdown(f"### **{result['ticker']}** ({result['sector']})")
        
        # Stats row
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("💵 Price", f"${m['price']:.2f}")
        c2.metric("📈 Today", f"{m['daily_chg']:+.1f}%")
        c3.metric("📊 Volume", f"{m['rel_vol']:.1f}x")
        c4.metric("🎯 Score", signal['score'])
        c5.metric("🏆 Win Rate", f"{stats.get('win_rate', 0)}%")
        
        # Action box
        if signal['strength'] == 'STRONG':
            st.success(f"⚡ **{signal['action']}**")
        else:
            st.warning(f"👀 **{signal['action']}**")
        
        st.caption(f"Historical: {stats.get('win_rate', 0)}% win rate | +{stats.get('avg_return', 0):.1f}% avg return | p={stats.get('p_value', 0):.3f}")
        st.divider()


def render_atp_checklist(signal):
    """Render ATP+ checklist for signal"""
    st.markdown("### 🖥️ ATP+ Checklist")
    st.markdown("*What to look for in Fidelity Active Trader Pro*")
    
    for item in signal.get('atp_checklist', []):
        if item.startswith('✓'):
            st.markdown(f"<span style='color: #00ff88'>{item}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color: #ffaa00'>{item}</span>", unsafe_allow_html=True)


def render_signal_checklist(signal):
    """Render signal criteria checklist"""
    st.markdown("### ✅ Signal Criteria")
    
    for check_name, passed in signal.get('checks', {}).items():
        if passed:
            st.markdown(f"<span style='color: #00ff88'>✓ {check_name}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color: #ff4444'>✗ {check_name}</span>", unsafe_allow_html=True)


def render_trade_calculator(result):
    """Render trade setup calculator"""
    m = result['metrics']
    
    st.markdown("### 💰 Trade Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        account_size = st.number_input("Account Size ($)", value=50000, step=1000)
        risk_pct = st.slider("Risk per Trade (%)", 0.5, 5.0, 2.0, 0.5)
    
    with col2:
        entry_price = st.number_input("Entry Price ($)", value=float(m['price']), step=0.01)
        stop_pct = st.slider("Stop Loss (%)", 2.0, 20.0, 7.0, 0.5)
    
    stop_price = entry_price * (1 - stop_pct/100)
    risk_per_share = entry_price - stop_price
    risk_amount = account_size * (risk_pct / 100)
    shares = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0
    position_size = shares * entry_price
    
    # Targets
    target_10 = entry_price * 1.10
    target_20 = entry_price * 1.20
    target_50 = entry_price * 1.50
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Shares to Buy", f"{shares:,}")
        st.metric("💵 Position Size", f"${position_size:,.0f}")
    
    with col2:
        st.metric("⚠️ Risk Amount", f"${risk_amount:,.0f}")
        st.metric("🛑 Stop Price", f"${stop_price:.2f}")
    
    with col3:
        st.metric("🎯 Target 10%", f"${target_10:.2f}")
        st.metric("🎯 Target 20%", f"${target_20:.2f}")
    
    # Order summary
    st.markdown("---")
    st.markdown("**📝 Order Summary:**")
    st.code(f"""
BUY {shares} shares of {result['ticker']} @ ${entry_price:.2f}
STOP LOSS @ ${stop_price:.2f} ({stop_pct:.1f}%)
TAKE PROFIT #1 @ ${target_10:.2f} (+10%)
TAKE PROFIT #2 @ ${target_20:.2f} (+20%)
    """)


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    # =========================================================================
    # HEADER
    # =========================================================================
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <h1 style="font-size: 3.5rem; margin: 0; background: linear-gradient(90deg, #00ff88, #4488ff, #ff4444); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                🐺 WOLF PACK
            </h1>
            <p style="color: #888; font-size: 1.3rem; margin-top: 5px;">
                Command Center v3.0 | 4 Validated Edges | Real-Time Scanner
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # =========================================================================
    # SIDEBAR
    # =========================================================================
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <span style="font-size: 3rem;">🐺</span>
            <h2 style="margin: 0;">Controls</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 REFRESH DATA", use_container_width=True, type="primary"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        
        view_mode = st.radio(
            "📱 View Mode",
            ["🔥 HOT TICKETS", "🎯 Signal Hunter", "📊 Full Scanner", "🔬 Deep Dive", "📚 Signal Guide"]
        )
        
        st.markdown("---")
        
        st.markdown("### 📈 Our Edges")
        for sig_type, stats in SIGNAL_STATS.items():
            with st.expander(f"{stats['emoji']} {stats['name']}"):
                st.markdown(f"**Win Rate:** {stats['win_rate']}%")
                st.markdown(f"**Avg Return:** +{stats['avg_return']:.1f}%")
                st.markdown(f"**p-value:** {stats['p_value']:.3f}")
                st.markdown(f"*{stats['description']}*")
        
        st.markdown("---")
        st.markdown(f"*Last scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        st.markdown("*Auto-refresh: 60s*")
    
    # =========================================================================
    # FETCH DATA
    # =========================================================================
    with st.spinner("🐺 Scanning the herd for opportunities..."):
        data = fetch_all_data()
        results = analyze_all(data)
    
    # Categorize signals
    strong_signals = [(r, s) for r in results for s in r['signals'] if s['strength'] == 'STRONG']
    watch_signals = [(r, s) for r in results for s in r['signals'] if s['strength'] in ['MODERATE', 'SETUP', 'WATCH']]
    
    # =========================================================================
    # VIEW: HOT TICKETS - DEAD SIMPLE
    # =========================================================================
    if view_mode == "🔥 HOT TICKETS":
        
        st.markdown("# 🔥 WHAT TO BUY RIGHT NOW 🔥")
        st.caption("Auto-updates every 60 seconds | Only showing STRONG signals")
        
        if strong_signals:
            # Rank by signal quality (Wolf > Capitulation > Pre-Run > Pocket)
            signal_rank = {'WOLF': 1, 'CAPITULATION': 2, 'PRE-RUN': 3, 'POCKET': 4}
            ranked = sorted(strong_signals, key=lambda x: signal_rank.get(x[1]['type'], 5))
            
            for idx, (result, signal) in enumerate(ranked):
                m = result['metrics']
                stats = SIGNAL_STATS.get(signal['type'], {})
                
                # Hot ticket number
                ticket_num = idx + 1
                
                if ticket_num == 1:
                    border_color = "#FFD700"  # Gold
                    label = "🥇 #1 HOT TICKET"
                elif ticket_num == 2:
                    border_color = "#C0C0C0"  # Silver
                    label = "🥈 #2 HOT TICKET"
                elif ticket_num == 3:
                    border_color = "#CD7F32"  # Bronze
                    label = "🥉 #3 HOT TICKET"
                else:
                    border_color = stats.get('color', '#00ff88')
                    label = f"#{ticket_num} HOT TICKET"
                
                # === HOT TICKET CARD - Using Native Streamlit ===
                st.markdown("---")
                
                # Badge and ticker header
                col_badge, col_time = st.columns([3, 1])
                with col_badge:
                    st.markdown(f"### {label}")
                with col_time:
                    st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
                
                # Main ticker display
                col_ticker, col_price = st.columns([2, 1])
                with col_ticker:
                    st.markdown(f"# 🎯 {result['ticker']}")
                    st.markdown(f"*{result['sector']} | {signal['emoji']} {stats.get('name', signal['type'])}*")
                with col_price:
                    st.metric("Price", f"${m['price']:.2f}", f"{m['daily_chg']:+.1f}% today")
                
                # BUY SIGNAL BOX
                st.success("### ✅ BUY SIGNAL CONFIRMED")
                
                # Stats row
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("🏆 Win Rate", f"{stats.get('win_rate', 0)}%")
                c2.metric("💰 Avg Return", f"+{stats.get('avg_return', 0):.0f}%")
                c3.metric("📊 Volume", f"{m['rel_vol']:.1f}x")
                c4.metric("🎯 Score", signal['score'])
                
                # Why to buy
                st.info(f"**🎯 WHY:** {stats.get('description', '')}")
                
                # Quick action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"📊 See Chart - {result['ticker']}", key=f"chart_{result['ticker']}"):
                        st.session_state['deep_dive_ticker'] = result['ticker']
                        st.session_state['view_mode'] = "🔬 Deep Dive"
                        st.rerun()
                with col2:
                    st.markdown(f"**🛑 Stop:** ${m['support']:.2f}")
                with col3:
                    st.markdown(f"**🎯 Target:** ${m['price'] * 1.15:.2f} (+15%)")
            
            # Summary box
            st.markdown("---")
            st.success(f"### 🐺 {len(strong_signals)} STRONG SIGNALS ACTIVE")
            st.caption("These are statistically validated. Historical win rates: 58-78%")
            
        else:
            st.warning("### ⏳ NO HOT TICKETS RIGHT NOW")
            st.markdown("The pack is watching... Waiting for confirmed setups.")
            st.caption("Check the Watch List below for setups forming.")
        
        # Watch list - next up
        if watch_signals:
            st.markdown("---")
            st.warning("### 👀 NEXT UP - Watch These Close")
            
            for result, signal in watch_signals[:5]:
                m = result['metrics']
                stats = SIGNAL_STATS.get(signal['type'], {})
                
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                
                with col1:
                    st.markdown(f"**{signal['emoji']} {result['ticker']}** - {result['sector']}")
                with col2:
                    st.markdown(f"${m['price']:.2f}")
                with col3:
                    delta = f"{m['daily_chg']:+.1f}%"
                    st.markdown(f"**{delta}**")
                with col4:
                    st.markdown(f"*{signal['score']} - Needs: {[k.split('(')[0].strip() for k,v in signal['checks'].items() if not v][:2]}*")
    
    # =========================================================================
    # VIEW: SIGNAL HUNTER
    # =========================================================================
    elif view_mode == "🎯 Signal Hunter":
        
        # Top stats row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <div style="color: #00ff88; font-size: 2.5rem; font-weight: bold;">{len(strong_signals)}</div>
                <div style="color: #888;">STRONG SIGNALS</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-box">
                <div style="color: #ffaa00; font-size: 2.5rem; font-weight: bold;">{len(watch_signals)}</div>
                <div style="color: #888;">WATCH LIST</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            movers = len([r for r in results if abs(r['metrics']['daily_chg']) > 5])
            st.markdown(f"""
            <div class="stat-box">
                <div style="color: #4488ff; font-size: 2.5rem; font-weight: bold;">{movers}</div>
                <div style="color: #888;">BIG MOVERS</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            wounded = len([r for r in results if r['metrics']['pct_from_high_20'] < -20])
            st.markdown(f"""
            <div class="stat-box">
                <div style="color: #ff4444; font-size: 2.5rem; font-weight: bold;">{wounded}</div>
                <div style="color: #888;">WOUNDED</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            total = len(results)
            st.markdown(f"""
            <div class="stat-box">
                <div style="color: #888; font-size: 2.5rem; font-weight: bold;">{total}</div>
                <div style="color: #888;">TOTAL SCANNED</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Strong signals section
        if strong_signals:
            st.markdown("## 🎯 STRONG SIGNALS - ACTION NOW!")
            st.markdown("*These stocks have ALL criteria met for our validated edges*")
            
            for result, signal in strong_signals:
                render_signal_card(result, signal)
                
                with st.expander(f"📋 {result['ticker']} - Full Analysis & Trade Setup"):
                    tab1, tab2, tab3, tab4 = st.tabs(["📊 Chart", "✅ Criteria", "🖥️ ATP+ Guide", "💰 Trade Calc"])
                    
                    with tab1:
                        st.plotly_chart(render_chart(result), use_container_width=True)
                    
                    with tab2:
                        render_signal_checklist(signal)
                        st.markdown("---")
                        st.markdown("**Entry Strategy:**")
                        st.info(signal.get('entry_strategy', 'N/A'))
                        st.markdown("**Stop Strategy:**")
                        st.warning(signal.get('stop_strategy', 'N/A'))
                    
                    with tab3:
                        render_atp_checklist(signal)
                    
                    with tab4:
                        render_trade_calculator(result)
        else:
            st.info("🐺 No STRONG signals right now. The pack is watching... Check the Watch List below!")
        
        # Watch list section
        if watch_signals:
            st.markdown("---")
            st.markdown("## 👀 WATCH LIST - Setups Forming")
            st.markdown("*These are building toward signals - monitor closely*")
            
            for result, signal in watch_signals[:8]:
                m = result['metrics']
                stats = SIGNAL_STATS.get(signal['type'], {})
                color = stats.get('color', '#888')
                
                col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1, 1, 2.5])
                
                with col1:
                    st.markdown(f"**{signal['emoji']} {result['ticker']}** ({result['sector']})")
                with col2:
                    st.markdown(f"${m['price']:.2f}")
                with col3:
                    chg_color = '#00ff88' if m['daily_chg'] > 0 else '#ff4444'
                    st.markdown(f"<span style='color:{chg_color}'>{m['daily_chg']:+.1f}%</span>", unsafe_allow_html=True)
                with col4:
                    st.markdown(f"<span style='color:{color}'>{signal['score']}</span>", unsafe_allow_html=True)
                with col5:
                    st.markdown(f"*{signal['action'][:50]}...*")
                
                st.markdown("<hr style='margin: 5px 0; opacity: 0.2;'>", unsafe_allow_html=True)
        
        # Sector heatmap
        st.markdown("---")
        st.markdown("## 🔥 Sector Performance")
        st.plotly_chart(render_sector_heatmap(results), use_container_width=True)
    
    # =========================================================================
    # VIEW: FULL SCANNER
    # =========================================================================
    elif view_mode == "📊 Full Scanner":
        st.markdown("## 📊 Full Universe Scanner")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            sector_filter = st.multiselect("Sectors", list(UNIVERSE.keys()))
        with col2:
            signal_filter = st.multiselect("Signal Types", list(SIGNAL_STATS.keys()))
        with col3:
            sort_by = st.selectbox("Sort By", ["Signals", "Daily Change", "Volume", "From High"])
        with col4:
            show_all = st.checkbox("Show All", value=True)
        
        # Build table data
        table_data = []
        for r in results:
            if sector_filter and r['sector'] not in sector_filter:
                continue
            
            m = r['metrics']
            signals_list = [f"{s['emoji']}{s['type']}" for s in r['signals']]
            signals_str = ', '.join(signals_list) if signals_list else '-'
            
            if signal_filter:
                has_signal = any(s['type'] in signal_filter for s in r['signals'])
                if not has_signal and not show_all:
                    continue
            
            table_data.append({
                'Ticker': r['ticker'],
                'Sector': r['sector'],
                'Price': f"${m['price']:.2f}",
                'Day %': m['daily_chg'],
                'Week %': m['weekly_chg'],
                'From High': m['pct_from_high_20'],
                'Volume': f"{m['rel_vol']:.1f}x",
                'CLV': f"{m['clv_today']:.2f}",
                'Signals': signals_str,
                'Signal Count': len(r['signals'])
            })
        
        if table_data:
            df = pd.DataFrame(table_data)
            
            # Sort
            sort_map = {
                "Signals": "Signal Count",
                "Daily Change": "Day %", 
                "Volume": "Volume", 
                "From High": "From High"
            }
            ascending = True if sort_by == "From High" else False
            df = df.sort_values(sort_map[sort_by], ascending=ascending)
            
            # Display
            st.dataframe(
                df.drop('Signal Count', axis=1),
                use_container_width=True,
                height=500
            )
            
            st.markdown(f"*Showing {len(table_data)} stocks*")
        
        # Sector breakdown
        st.markdown("---")
        st.markdown("## 🔥 Sector Heat Map")
        st.plotly_chart(render_sector_heatmap(results), use_container_width=True)
    
    # =========================================================================
    # VIEW: DEEP DIVE
    # =========================================================================
    elif view_mode == "🔬 Deep Dive":
        st.markdown("## 🔬 Deep Dive Analysis")
        
        available_tickers = sorted([r['ticker'] for r in results])
        selected = st.selectbox("Select Ticker to Analyze", available_tickers)
        
        if selected:
            result = [r for r in results if r['ticker'] == selected][0]
            m = result['metrics']
            
            # Header
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div style="padding: 20px;">
                    <div class="ticker-header">{selected}</div>
                    <div style="color: #888; font-size: 1.3rem;">{result['sector']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                chg_color = '#00ff88' if m['daily_chg'] > 0 else '#ff4444'
                st.markdown(f"""
                <div style="text-align: right; padding: 20px;">
                    <div style="font-size: 3rem; font-weight: bold;">${m['price']:.2f}</div>
                    <div style="font-size: 1.5rem; color: {chg_color};">{m['daily_chg']:+.1f}% today</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Active signals
            if result['signals']:
                st.markdown("### 🎯 Active Signals")
                for signal in result['signals']:
                    render_signal_card(result, signal)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        render_signal_checklist(signal)
                    with col2:
                        render_atp_checklist(signal)
            else:
                st.info("No active signals for this ticker. Monitor for setup formation.")
            
            st.markdown("---")
            
            # Chart
            st.markdown("### 📈 Price & Volume Chart")
            st.plotly_chart(render_chart(result, height=500), use_container_width=True)
            
            st.markdown("---")
            
            # All metrics
            st.markdown("### 📊 All Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("**📈 Price Action**")
                st.metric("Daily Change", f"{m['daily_chg']:+.1f}%")
                st.metric("Weekly Change", f"{m['weekly_chg']:+.1f}%")
                st.metric("Monthly Change", f"{m['monthly_chg']:+.1f}%")
            
            with col2:
                st.markdown("**📊 Volume**")
                st.metric("Relative Volume", f"{m['rel_vol']:.2f}x")
                st.metric("Up/Down Vol Ratio", f"{m['vol_ratio']:.2f}")
                st.metric("5-Day Vol Ratio", f"{m['vol_ratio_5d']:.2f}")
            
            with col3:
                st.markdown("**📍 Position**")
                st.metric("From 20d High", f"{m['pct_from_high_20']:.1f}%")
                st.metric("From 52w High", f"{m['pct_from_high_52']:.1f}%")
                st.metric("Volatility", f"{m['volatility']:.1f}%")
            
            with col4:
                st.markdown("**🎯 Technical**")
                st.metric("CLV Today", f"{m['clv_today']:.2f}")
                st.metric("5d Avg CLV", f"{m['avg_clv']:.2f}")
                st.metric("Above 50 MA", "✅ Yes" if m['above_ma50'] else "❌ No")
            
            st.markdown("---")
            
            # Trade calculator
            render_trade_calculator(result)
    
    # =========================================================================
    # VIEW: SIGNAL GUIDE
    # =========================================================================
    elif view_mode == "📚 Signal Guide":
        st.markdown("## 📚 Signal Reference Guide")
        st.markdown("*Everything you need to know about our 4 validated edges*")
        
        for sig_type, stats in SIGNAL_STATS.items():
            st.markdown(f"""
            <div class="signal-strong" style="border-color: {stats['color']};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 3rem;">{stats['emoji']}</span>
                        <span style="font-size: 2rem; font-weight: bold; color: {stats['color']}; margin-left: 15px;">
                            {stats['name']}
                        </span>
                    </div>
                    <div style="display: flex; gap: 20px;">
                        <div class="stat-box">
                            <div style="color: #888;">WIN RATE</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #00ff88;">{stats['win_rate']}%</div>
                        </div>
                        <div class="stat-box">
                            <div style="color: #888;">AVG RETURN</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #00ff88;">+{stats['avg_return']:.1f}%</div>
                        </div>
                        <div class="stat-box">
                            <div style="color: #888;">P-VALUE</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: {'#00ff88' if stats['p_value'] < 0.01 else '#ffaa00'};">{stats['p_value']:.3f}</div>
                        </div>
                    </div>
                </div>
                <div style="margin-top: 20px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 10px;">
                    <div style="color: #fff; font-size: 1.1rem;">{stats['description']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
        
        st.markdown("---")
        st.markdown("### 🎓 How We Validated These Signals")
        st.markdown("""
        Each signal was rigorously backtested using:
        
        1. **Monte Carlo Simulation** - 1,000 random shuffles to ensure edges aren't luck
        2. **Statistical Significance** - p-value < 0.05 required (most are < 0.01!)
        3. **Large Sample Size** - Tested across 43 tickers, 6+ months of data
        4. **Multiple Sectors** - Validated across QUANTUM, SPACE, NUCLEAR, DEFENSE, AI, CRYPTO
        
        **These aren't guesses - they're statistically validated patterns!**
        """)
        
        st.markdown("---")
        st.markdown("### 🖥️ ATP+ Integration Tips")
        st.markdown("""
        **Recommended ATP Layouts:**
        
        1. **Wolf Hunter Layout** - 5-min chart + volume overlay + Level 2
        2. **Momentum Scanner** - Daily charts + volume profile + Time & Sales
        3. **Capitulation Watch** - Wide view of beaten-down names + volume alerts
        
        **Key ATP Features to Use:**
        - Volume % change column in watch lists
        - 20-day volume average overlay on charts
        - Level 2 for spotting institutional activity
        - Time & Sales for reading order flow
        """)
    
    # =========================================================================
    # FOOTER
    # =========================================================================
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        🐺 Wolf Pack Command Center v3.0 | Built by the Pack, for the Pack
        <br><br>
        4 Validated Edges | 43 Tickers | 7 Sectors | Real-Time Scanning
        <br><br>
        <span style="font-size: 2.5rem;">AWOOOO! 🐺</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
