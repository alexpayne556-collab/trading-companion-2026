#!/usr/bin/env python3
"""
🐺 WOLF PACK WEB DASHBOARD
===========================
The most badass trading dashboard the pack has ever seen.

Features:
- Real-time 8-K contract scanner
- Cross-signal conviction scores
- Wounded prey tracker
- Pattern cycle analysis
- AI Fuel Chain heatmap
- Insider cluster detection
- Congress trades
- Live price updates
- Beautiful charts

AWOOOO 🐺 LLHR
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import sys

# Add tools to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))

app = Flask(__name__)
CORS(app)

# =============================================================================
# AI FUEL CHAIN CONFIG
# =============================================================================

AI_FUEL_CHAIN = {
    'NUCLEAR': ['UUUU', 'SMR', 'LEU', 'OKLO', 'CCJ', 'DNN', 'UEC', 'NXE', 'NNE'],
    'UTILITIES': ['NEE', 'VST', 'CEG', 'WMB'],
    'COOLING': ['VRT', 'MOD', 'NVT'],
    'PHOTONICS': ['LITE', 'AAOI', 'COHR', 'GFS'],
    'NETWORKING': ['ANET', 'CRDO', 'FN', 'CIEN'],
    'STORAGE': ['MU', 'WDC', 'STX'],
    'CHIPS': ['AMD', 'MRVL', 'AVGO', 'INTC', 'AMKR'],
    'DC_BUILDERS': ['SMCI', 'EME', 'CLS', 'FIX'],
    'DC_REITS': ['EQIX', 'DLR'],
    'QUANTUM': ['IONQ', 'RGTI', 'QBTS', 'QUBT', 'ARQQ'],
    'SPACE': ['LUNR', 'RKLB', 'RDW', 'ASTS', 'SIDU', 'BKSY', 'PL'],
    'AI_SOFTWARE': ['PLTR', 'AI', 'SOUN', 'PATH', 'UPST']
}

PRIORITY_TICKERS = ['UUUU', 'SIDU', 'LUNR', 'MU', 'LITE', 'VRT', 'SMR', 'LEU', 'RDW', 'OKLO']

# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/heatmap')
def get_heatmap():
    """Get AI Fuel Chain heatmap data"""
    try:
        heatmap_data = []
        
        for sector, tickers in AI_FUEL_CHAIN.items():
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period='5d')
                    
                    if len(hist) >= 2:
                        current = hist['Close'].iloc[-1]
                        prev = hist['Close'].iloc[-2]
                        change_1d = ((current - prev) / prev) * 100
                        
                        # 5-day change
                        if len(hist) >= 5:
                            change_5d = ((current - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                        else:
                            change_5d = change_1d
                        
                        volume = hist['Volume'].iloc[-1]
                        avg_volume = hist['Volume'].mean()
                        vol_ratio = volume / avg_volume if avg_volume > 0 else 1
                        
                        heatmap_data.append({
                            'ticker': ticker,
                            'sector': sector,
                            'price': round(current, 2),
                            'change_1d': round(change_1d, 2),
                            'change_5d': round(change_5d, 2),
                            'volume': int(volume),
                            'vol_ratio': round(vol_ratio, 2),
                            'priority': ticker in PRIORITY_TICKERS
                        })
                except:
                    continue
        
        return jsonify({'status': 'success', 'data': heatmap_data})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/conviction/<ticker>')
def get_conviction(ticker):
    """Get cross-signal conviction score for ticker"""
    try:
        # Import scanner functions
        from cross_signal_validator import validate_ticker
        
        result = validate_ticker(ticker)
        
        return jsonify({
            'status': 'success',
            'ticker': ticker,
            'conviction_score': result['total_score'],
            'signals_active': result['signals_active'],
            'wounded_score': result['wounded_score'],
            'insider_score': result['insider_score'],
            'contract_score': result['contract_score'],
            'thesis_score': result['thesis_score'],
            'wounded_details': result['wounded'],
            'insider_details': result['insider'],
            'contract_details': result['contract']
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/wounded_prey')
def get_wounded_prey():
    """Get wounded prey scanner results"""
    try:
        from wounded_prey_scanner import scan_wounded_prey
        
        results = scan_wounded_prey()
        
        # Convert to JSON-serializable format
        prey_data = []
        for r in results:
            prey_data.append({
                'ticker': r['ticker'],
                'sector': r['sector'],
                'price': round(r['price'], 2),
                'pct_from_high': round(r['pct_from_high'], 1),
                'change_5d': round(r['change_5d'], 1),
                'change_10d': round(r['change_10d'], 1),
                'vol_ratio': round(r['vol_ratio'], 2),
                'bounce_score': r['bounce_score']
            })
        
        return jsonify({'status': 'success', 'data': prey_data})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/clusters')
def get_clusters():
    """Get insider cluster data"""
    try:
        from cluster_buy_scanner import scan_all_clusters
        
        results = scan_all_clusters(days=90)
        
        # Convert to JSON format
        cluster_data = []
        for r in results:
            if r['classification'] != 'NO_CLUSTER':
                cluster_data.append({
                    'ticker': r['ticker'],
                    'sector': r['sector'],
                    'classification': r['classification'],
                    'unique_buyers': r['unique_buyers'],
                    'total_purchases': r['total_purchases'],
                    'c_suite_count': r['c_suite_count'],
                    'total_value': r['total_value'],
                    'date_range_days': r['date_range_days'],
                    'cluster_score': r['cluster_score']
                })
        
        return jsonify({'status': 'success', 'data': cluster_data})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/price/<ticker>')
def get_price(ticker):
    """Get current price and chart data for ticker"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='3mo')
        
        if hist.empty:
            return jsonify({'status': 'error', 'message': 'No data found'})
        
        current = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        change = ((current - prev_close) / prev_close) * 100
        
        # Chart data
        chart_data = []
        for date, row in hist.iterrows():
            chart_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'close': round(row['Close'], 2),
                'volume': int(row['Volume'])
            })
        
        return jsonify({
            'status': 'success',
            'ticker': ticker,
            'price': round(current, 2),
            'change': round(change, 2),
            'chart_data': chart_data
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/high_conviction')
def get_high_conviction():
    """Get all high conviction setups (70+)"""
    try:
        from cross_signal_validator import scan_all_tickers
        
        results = scan_all_tickers(min_signals=2)
        
        # Filter for high conviction
        high_conviction = [r for r in results if r['total_score'] >= 70]
        
        conviction_data = []
        for r in high_conviction:
            conviction_data.append({
                'ticker': r['ticker'],
                'sector': r['thesis']['sector'],
                'total_score': r['total_score'],
                'signals_active': r['signals_active'],
                'wounded_score': r['wounded_score'],
                'insider_score': r['insider_score'],
                'contract_score': r['contract_score'],
                'thesis_score': r['thesis_score']
            })
        
        # Sort by score
        conviction_data.sort(key=lambda x: x['total_score'], reverse=True)
        
        return jsonify({'status': 'success', 'data': conviction_data})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/8k_scan')
def scan_8k():
    """Scan for recent 8-K filings"""
    try:
        from sec_8k_contract_scanner import get_recent_8k_filings, score_filing
        
        filings = get_recent_8k_filings(hours=24)
        
        results = []
        for filing in filings[:20]:  # Top 20
            ticker = filing.get('ticker', '')
            url = filing.get('url', '')
            
            if ticker:
                # Try to score it
                from sec_8k_contract_scanner import extract_filing_text
                text = extract_filing_text(url)
                
                if text:
                    score, matches = score_filing(text, ticker)
                    
                    if score >= 30:  # Minimum threshold
                        results.append({
                            'ticker': ticker,
                            'score': score,
                            'filed_time': filing.get('filed', ''),
                            'url': url,
                            'matches': matches
                        })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return jsonify({'status': 'success', 'data': results})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🐺 WOLF PACK WEB DASHBOARD STARTING")
    print("="*80)
    print(f"\n   Opening in browser: http://localhost:5000")
    print(f"   Press CTRL+C to stop\n")
    print("="*80 + "\n")
    
    # Run server
    app.run(host='0.0.0.0', port=5000, debug=True)
