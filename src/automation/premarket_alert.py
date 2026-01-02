#!/usr/bin/env python3
"""
🐺 PRE-MARKET ALERT
Runs at 6:30 AM EST (GitHub Actions cron)
Checks AISP pre-market price, volume, entry conditions
WAKES YOU UP if entry zone active or abort conditions met
"""

import os
import json
import requests
from datetime import datetime
import yfinance as yf

# Configuration
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK', '')
PRIMARY_TARGET = 'AISP'
ENTRY_LOW = 2.70
ENTRY_HIGH = 2.90
ABORT_GAP_UP = 3.15  # If gaps above this, abort
ABORT_GAP_DOWN = 2.50  # If gaps below this, wait/reassess

def send_discord_alert(message, wake_up=False):
    """Send alert to Discord webhook"""
    if not DISCORD_WEBHOOK:
        print("⚠️ No Discord webhook configured")
        return
    
    # Format message
    if wake_up:
        content = f"@everyone ⏰ **WAKE UP TYR** ⏰\n\n{message}"
    else:
        content = f"🐺 **Pre-Market Update**\n\n{message}"
    
    payload = {
        "content": content,
        "username": "Wolf Pack Alert"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload)
        if response.status_code == 204:
            print("✅ Discord alert sent")
        else:
            print(f"⚠️ Discord alert failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Discord error: {e}")

def get_premarket_data(ticker):
    """Get pre-market price and volume"""
    try:
        stock = yf.Ticker(ticker)
        
        # Get previous close
        hist = stock.history(period='5d')
        if hist.empty or len(hist) < 2:
            return None
        
        prev_close = hist['Close'].iloc[-1]
        
        # Get current price (pre-market if available)
        info = stock.info
        current = info.get('currentPrice', prev_close)
        
        # Calculate gap
        gap_pct = ((current - prev_close) / prev_close) * 100
        
        # Get 52-week range
        low_52w = info.get('fiftyTwoWeekLow', 0)
        high_52w = info.get('fiftyTwoWeekHigh', 0)
        
        return {
            'ticker': ticker,
            'prev_close': round(prev_close, 2),
            'current': round(current, 2),
            'gap_pct': round(gap_pct, 2),
            'low_52w': round(low_52w, 2),
            'high_52w': round(high_52w, 2),
            'volume': info.get('volume', 0),
            'avg_volume': info.get('averageVolume', 0)
        }
        
    except Exception as e:
        print(f"❌ Error getting data for {ticker}: {e}")
        return None

def analyze_entry_conditions(data):
    """Analyze if entry conditions are met"""
    if not data:
        return {'status': 'ERROR', 'message': 'No data'}
    
    current = data['current']
    gap_pct = data['gap_pct']
    
    # ABORT CONDITIONS
    if current > ABORT_GAP_UP:
        return {
            'status': 'ABORT',
            'reason': 'GAP UP',
            'message': f"🚨 ABORT: {data['ticker']} gapped to ${current} (>{ABORT_GAP_UP})\n**TOO EXPENSIVE - Pivot to SOUN backup**"
        }
    
    if current < ABORT_GAP_DOWN:
        return {
            'status': 'WAIT',
            'reason': 'GAP DOWN',
            'message': f"⚠️ WAIT: {data['ticker']} at ${current} (<{ABORT_GAP_DOWN})\nWatch for support. May be better entry."
        }
    
    # ENTRY ZONE ACTIVE
    if ENTRY_LOW <= current <= ENTRY_HIGH:
        return {
            'status': 'GO',
            'reason': 'ENTRY ZONE',
            'message': f"🎯 GO GO GO: {data['ticker']} at ${current}\n**ENTRY ZONE ACTIVE** (${ENTRY_LOW}-${ENTRY_HIGH})\n9:45 AM execution window ready!"
        }
    
    # JUST ABOVE ENTRY ZONE
    if ENTRY_HIGH < current <= ENTRY_HIGH + 0.20:
        return {
            'status': 'READY',
            'reason': 'NEAR ENTRY',
            'message': f"🟡 READY: {data['ticker']} at ${current}\nSlightly above entry zone. Watch for dip at open."
        }
    
    # JUST BELOW ENTRY ZONE
    if ENTRY_LOW - 0.20 <= current < ENTRY_LOW:
        return {
            'status': 'READY',
            'reason': 'NEAR ENTRY',
            'message': f"🟡 READY: {data['ticker']} at ${current}\nSlightly below entry zone. Good setup if holds."
        }
    
    # OUTSIDE RANGE
    return {
        'status': 'WATCH',
        'reason': 'OUT OF RANGE',
        'message': f"📊 WATCH: {data['ticker']} at ${current}\nOutside entry zone. Monitor at open."
    }

def main():
    """Main pre-market alert routine"""
    print("=" * 60)
    print("🐺 PRE-MARKET ALERT - Wolf Pack Trading")
    print("=" * 60)
    print(f"Alert time: {datetime.now().strftime('%Y-%m-%d %I:%M %p EST')}")
    print()
    
    # Get pre-market data
    print(f"📊 Checking {PRIMARY_TARGET} pre-market...")
    data = get_premarket_data(PRIMARY_TARGET)
    
    if not data:
        print("❌ Failed to get pre-market data")
        send_discord_alert("❌ Pre-market scan failed - check manually!", wake_up=True)
        return
    
    # Display data
    print(f"\n{PRIMARY_TARGET} PRE-MARKET:")
    print(f"  Previous close: ${data['prev_close']}")
    print(f"  Current price:  ${data['current']}")
    print(f"  Gap: {data['gap_pct']:+.1f}%")
    print(f"  52W range: ${data['low_52w']} - ${data['high_52w']}")
    
    # Analyze entry conditions
    analysis = analyze_entry_conditions(data)
    
    print(f"\n📊 STATUS: {analysis['status']}")
    print(f"  Reason: {analysis['reason']}")
    print()
    print(analysis['message'])
    
    # Save results
    log_file = f"logs/premarket_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs('logs', exist_ok=True)
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'data': data,
        'analysis': analysis
    }
    
    with open(log_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n📁 Results saved: {log_file}")
    
    # Send alert based on status
    wake_up = analysis['status'] in ['GO', 'ABORT', 'ERROR']
    send_discord_alert(analysis['message'], wake_up=wake_up)
    
    print("\n🐺 Pre-market alert complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
