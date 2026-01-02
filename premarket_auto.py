#!/usr/bin/env python3
"""
🐺 PRE-MARKET AUTO SCANNER - Autonomous pre-market monitoring

Runs automatically at 6:00 AM and 8:30 AM ET via cron.
Generates GO/NO-GO decisions for each ticker.

Author: Brokkr
Date: January 2, 2026
"""

import yfinance as yf
import yaml
import json
from datetime import datetime
from pathlib import Path

def load_config():
    """Load wolf den configuration."""
    with open("wolf_den_config.yaml", "r") as f:
        return yaml.safe_load(f)

def check_premarket_price(ticker, config):
    """
    Check pre-market price and volume.
    
    Returns: {
        "price": float,
        "change_pct": float,
        "volume": int,
        "status": "GO"/"WAIT"/"ABORT"
    }
    """
    print(f"\n🔍 Checking {ticker} pre-market...")
    
    try:
        stock = yf.Ticker(ticker)
        
        # Get current price
        info = stock.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        prev_close = info.get('previousClose', 0)
        
        if prev_close == 0:
            return {
                "ticker": ticker,
                "error": "Unable to fetch price data",
                "status": "WAIT"
            }
        
        change_pct = ((current_price - prev_close) / prev_close) * 100
        
        # Get volume (if available in pre-market)
        hist = stock.history(period="1d", interval="1m")
        volume = int(hist['Volume'].sum()) if len(hist) > 0 else 0
        
        # Get entry zone from config
        entry_zone = config.get("entry_zones", {}).get(ticker, {})
        low_entry = entry_zone.get("low", 0)
        high_entry = entry_zone.get("high", 999999)
        
        # Determine status
        if current_price == 0:
            status = "WAIT"
            reason = "No price data yet"
        elif abs(change_pct) > config["thresholds"]["gap_up_alert"]:
            status = "ABORT"
            reason = f"Gap {change_pct:+.1f}% exceeds threshold"
        elif low_entry > 0 and (current_price < low_entry or current_price > high_entry):
            status = "WAIT"
            reason = f"Price ${current_price:.2f} outside entry zone ${low_entry}-${high_entry}"
        else:
            status = "GO"
            reason = "Price in range, no red flags"
        
        result = {
            "ticker": ticker,
            "price": current_price,
            "prev_close": prev_close,
            "change_pct": change_pct,
            "volume": volume,
            "status": status,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"   Price: ${current_price:.2f} ({change_pct:+.1f}%)")
        print(f"   Volume: {volume:,}")
        print(f"   Status: {status} - {reason}")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "ticker": ticker,
            "error": str(e),
            "status": "WAIT",
            "reason": "Error fetching data"
        }

def generate_report(results, config):
    """Generate human-readable report."""
    report = []
    report.append("=" * 70)
    report.append("🐺 PRE-MARKET SCANNER - STATUS UPDATE")
    report.append("=" * 70)
    
    now = datetime.now()
    report.append(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S ET')}")
    
    # Calculate time to market open (9:30 AM ET)
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    if now > market_open:
        report.append("Market: OPEN")
    else:
        delta = market_open - now
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        report.append(f"Market opens in: {hours}h {minutes}m")
    
    report.append("")
    
    # Primary ticker
    primary = config["watchlist"]["primary"]
    primary_result = next((r for r in results if r["ticker"] == primary), None)
    
    if primary_result:
        status = primary_result["status"]
        icon = "✅" if status == "GO" else "⚠️" if status == "WAIT" else "🔴"
        
        report.append(f"PRIMARY TARGET: {primary}")
        report.append(f"{icon} Status: {status}")
        
        if "price" in primary_result:
            report.append(f"   Price: ${primary_result['price']:.2f} ({primary_result['change_pct']:+.1f}%)")
            report.append(f"   Volume: {primary_result['volume']:,}")
        
        report.append(f"   {primary_result['reason']}")
        report.append("")
    
    # Backup tickers
    backups = config["watchlist"]["backup"]
    if backups:
        report.append("BACKUP TICKERS:")
        for ticker in backups:
            result = next((r for r in results if r["ticker"] == ticker), None)
            if result:
                status = result["status"]
                icon = "✅" if status == "GO" else "⚠️" if status == "WAIT" else "🔴"
                
                if "price" in result:
                    report.append(f"{icon} {ticker}: ${result['price']:.2f} ({result['change_pct']:+.1f}%) - {status}")
                else:
                    report.append(f"{icon} {ticker}: {status} - {result.get('reason', 'No data')}")
        report.append("")
    
    # Decision summary
    report.append("=" * 70)
    if primary_result and primary_result["status"] == "GO":
        report.append(f"✅ DECISION: PROCEED WITH {primary}")
        report.append(f"   Entry: ${primary_result['price']:.2f}")
        
        entry_zone = config.get("entry_zones", {}).get(primary, {})
        if "stop" in entry_zone:
            report.append(f"   Stop: ${entry_zone['stop']:.2f}")
        if "target_1" in entry_zone:
            report.append(f"   Target 1: ${entry_zone['target_1']:.2f}")
    
    elif primary_result and primary_result["status"] == "WAIT":
        report.append(f"⚠️  DECISION: WAIT ON {primary}")
        report.append(f"   {primary_result['reason']}")
        report.append(f"   Check again before market open")
    
    else:
        report.append(f"🔴 DECISION: ABORT {primary}")
        if primary_result:
            report.append(f"   {primary_result['reason']}")
        report.append(f"   Consider backup tickers or wait for better setup")
    
    report.append("=" * 70)
    
    return "\n".join(report)

def main():
    """Main pre-market scanning sequence."""
    print("\n🐺 WOLF DEN - PRE-MARKET SCANNER")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load config
    try:
        config = load_config()
    except FileNotFoundError:
        print("❌ wolf_den_config.yaml not found!")
        return 1
    
    # Build watchlist
    watchlist = [config["watchlist"]["primary"]] + config["watchlist"]["backup"]
    print(f"Watchlist: {', '.join(watchlist)}")
    
    # Scan each ticker
    results = []
    for ticker in watchlist:
        result = check_premarket_price(ticker, config)
        results.append(result)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path("logs") / f"premarket_{timestamp}.json"
    output_file.parent.mkdir(exist_ok=True)
    
    scan_data = {
        "timestamp": datetime.now().isoformat(),
        "watchlist": results
    }
    
    with open(output_file, "w") as f:
        json.dump(scan_data, f, indent=2)
    
    # Save latest
    latest_file = Path("logs") / "premarket_latest.json"
    with open(latest_file, "w") as f:
        json.dump(scan_data, f, indent=2)
    
    print(f"\n💾 Results saved: {output_file}")
    
    # Generate report
    report = generate_report(results, config)
    print("\n" + report)
    
    # Save report
    report_file = Path("logs") / f"premarket_{timestamp}.txt"
    with open(report_file, "w") as f:
        f.write(report)
    
    print("\n✅ Pre-market scan complete")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
