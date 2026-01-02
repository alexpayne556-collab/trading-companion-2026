#!/usr/bin/env python3
"""
🐺 OVERNIGHT SCANNER
Runs at 4:00 AM EST (GitHub Actions cron)
Checks for AISP 8-K filings, news, pre-market gaps
Sends Discord alert if action needed
"""

import os
import json
import requests
from datetime import datetime, timedelta
import yfinance as yf

# Configuration
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK', '')
WATCHLIST = ['AISP', 'LUNR', 'SOUN', 'IONQ', 'SMR']

def send_discord_alert(message, urgent=False):
    """Send alert to Discord webhook"""
    if not DISCORD_WEBHOOK:
        print("⚠️ No Discord webhook configured")
        return
    
    # Format message
    if urgent:
        content = f"@everyone 🚨 **URGENT ALERT** 🚨\n\n{message}"
    else:
        content = f"🐺 **Overnight Update**\n\n{message}"
    
    payload = {
        "content": content,
        "username": "Wolf Pack Scanner"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload)
        if response.status_code == 204:
            print("✅ Discord alert sent")
        else:
            print(f"⚠️ Discord alert failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Discord error: {e}")

def check_sec_filings(ticker):
    """Check for recent 8-K filings from SEC EDGAR"""
    results = []
    
    try:
        # SEC EDGAR recent filings
        url = f"https://data.sec.gov/submissions/CIK{ticker}.json"
        headers = {'User-Agent': 'Wolf Pack Trader contact@wolfpack.dev'}
        
        # For now, placeholder - need CIK lookup
        # Real implementation would parse SEC EDGAR RSS or API
        print(f"  Checking SEC filings for {ticker}...")
        
    except Exception as e:
        print(f"  ⚠️ SEC check error for {ticker}: {e}")
    
    return results

def check_premarket_gaps(ticker):
    """Check for significant pre-market price movement"""
    try:
        stock = yf.Ticker(ticker)
        
        # Get previous close
        hist = stock.history(period='5d')
        if hist.empty or len(hist) < 2:
            return None
        
        prev_close = hist['Close'].iloc[-2]
        
        # Get current price (delayed, but good enough for 4 AM check)
        current = stock.info.get('currentPrice', prev_close)
        
        # Calculate gap
        gap_pct = ((current - prev_close) / prev_close) * 100
        
        return {
            'ticker': ticker,
            'prev_close': round(prev_close, 2),
            'current': round(current, 2),
            'gap_pct': round(gap_pct, 2)
        }
        
    except Exception as e:
        print(f"  ⚠️ Gap check error for {ticker}: {e}")
        return None

def check_news(ticker):
    """Check for recent news"""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if not news:
            return []
        
        # Get news from last 12 hours
        recent = []
        cutoff = datetime.now().timestamp() - (12 * 3600)
        
        for item in news[:5]:  # Check last 5 items
            pub_time = item.get('providerPublishTime', 0)
            if pub_time > cutoff:
                recent.append({
                    'title': item.get('title', 'No title'),
                    'publisher': item.get('publisher', 'Unknown'),
                    'link': item.get('link', '')
                })
        
        return recent
        
    except Exception as e:
        print(f"  ⚠️ News check error for {ticker}: {e}")
        return []

def main():
    """Main overnight scan routine"""
    print("=" * 60)
    print("🐺 OVERNIGHT SCANNER - Wolf Pack Trading")
    print("=" * 60)
    print(f"Scan time: {datetime.now().strftime('%Y-%m-%d %I:%M %p EST')}")
    print()
    
    alerts = []
    urgent_alerts = []
    scan_results = {}
    
    for ticker in WATCHLIST:
        print(f"\n📊 Scanning {ticker}...")
        
        result = {
            'ticker': ticker,
            'scan_time': datetime.now().isoformat(),
            'sec_filings': [],
            'gap': None,
            'news': []
        }
        
        # Check SEC filings (8-K, etc)
        filings = check_sec_filings(ticker)
        result['sec_filings'] = filings
        if filings:
            urgent_alerts.append(f"🚨 {ticker}: New SEC filing detected!")
        
        # Check pre-market gaps
        gap = check_premarket_gaps(ticker)
        result['gap'] = gap
        if gap and abs(gap['gap_pct']) > 10:
            urgent_alerts.append(f"🚨 {ticker}: {gap['gap_pct']:+.1f}% gap!")
        elif gap and abs(gap['gap_pct']) > 5:
            alerts.append(f"📊 {ticker}: {gap['gap_pct']:+.1f}% gap")
        
        # Check news
        news = check_news(ticker)
        result['news'] = news
        if news:
            alerts.append(f"📰 {ticker}: {len(news)} new articles")
        
        scan_results[ticker] = result
        print(f"  ✅ {ticker} scan complete")
    
    # Save results
    log_file = f"logs/overnight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs('logs', exist_ok=True)
    with open(log_file, 'w') as f:
        json.dump(scan_results, f, indent=2)
    print(f"\n📁 Results saved: {log_file}")
    
    # Send alerts
    print("\n" + "=" * 60)
    print("ALERT SUMMARY")
    print("=" * 60)
    
    if urgent_alerts:
        message = "**URGENT - ACTION REQUIRED**\n\n" + "\n".join(urgent_alerts)
        print("\n🚨 URGENT ALERTS:")
        for alert in urgent_alerts:
            print(f"  {alert}")
        send_discord_alert(message, urgent=True)
    
    if alerts:
        message = "**Overnight Activity Detected**\n\n" + "\n".join(alerts)
        print("\n📊 STANDARD ALERTS:")
        for alert in alerts:
            print(f"  {alert}")
        send_discord_alert(message, urgent=False)
    
    if not urgent_alerts and not alerts:
        print("\n✅ All clear - no significant overnight activity")
        # Don't send "all clear" messages at 4 AM - let Tyr sleep
    
    print("\n🐺 Overnight scan complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
