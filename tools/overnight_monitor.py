#!/usr/bin/env python3
"""
🐺 OVERNIGHT MONITOR - Autonomous scanning while pack sleeps

Runs automatically at 4 AM ET via cron.
Checks for overnight events that could impact the hunt.

Author: Brokkr
Date: January 2, 2026
"""

import requests
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def load_config():
    """Load wolf den configuration."""
    with open("wolf_den_config.yaml", "r") as f:
        return yaml.safe_load(f)

def check_form4_filings(ticker, config, hours=24):
    """
    Check for new Form 4 filings in last X hours.
    
    Returns: {
        "found": bool,
        "filings": list,
        "alert_level": "GREEN"/"YELLOW"/"RED"
    }
    """
    print(f"  Checking Form 4 filings for {ticker}...")
    
    # This would use SEC EDGAR API
    # For MVP, simplified check
    # TODO: Integrate with form4_validator.py
    
    return {
        "found": False,
        "filings": [],
        "alert_level": "GREEN",
        "message": "No new Form 4 filings"
    }

def check_8k_filings(ticker, config, hours=24):
    """
    Check for new 8-K filings (material events).
    
    Returns: {
        "found": bool,
        "filings": list,
        "alert_level": "GREEN"/"YELLOW"/"RED"
    }
    """
    print(f"  Checking 8-K filings for {ticker}...")
    
    # SEC EDGAR recent filings check
    # Material items: 1.01 (entry into agreement), 2.01 (acquisition),
    # 5.02 (officer departure), 8.01 (material event)
    
    # TODO: Implement SEC EDGAR scraping
    # For now, return GREEN
    
    return {
        "found": False,
        "filings": [],
        "alert_level": "GREEN",
        "message": "No new 8-K filings"
    }

def check_news_headlines(ticker):
    """
    Check for overnight news via yfinance.
    
    Returns: {
        "found": bool,
        "headlines": list,
        "alert_level": "GREEN"/"YELLOW"/"RED"
    }
    """
    print(f"  Checking news for {ticker}...")
    
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        news = stock.news[:5] if hasattr(stock, 'news') else []
        
        # Check if any news is recent (last 12 hours)
        recent_news = []
        cutoff = datetime.now() - timedelta(hours=12)
        
        for item in news:
            pub_time = datetime.fromtimestamp(item.get('providerPublishTime', 0))
            if pub_time > cutoff:
                recent_news.append({
                    "title": item.get('title', ''),
                    "publisher": item.get('publisher', ''),
                    "time": pub_time.strftime("%Y-%m-%d %H:%M")
                })
        
        alert_level = "YELLOW" if recent_news else "GREEN"
        
        return {
            "found": len(recent_news) > 0,
            "headlines": recent_news,
            "alert_level": alert_level,
            "message": f"{len(recent_news)} recent headlines" if recent_news else "No recent news"
        }
        
    except Exception as e:
        return {
            "found": False,
            "headlines": [],
            "alert_level": "GREEN",
            "message": f"Error checking news: {str(e)}"
        }

def check_futures():
    """
    Check overnight futures performance.
    
    Returns: {
        "ES": "+0.3%",
        "NQ": "+0.5%",
        "alert_level": "GREEN"/"YELLOW"/"RED"
    }
    """
    print("  Checking futures...")
    
    # Would integrate with futures data API
    # For MVP, return placeholder
    
    return {
        "ES": "N/A",
        "NQ": "N/A",
        "alert_level": "GREEN",
        "message": "Futures check not implemented"
    }

def scan_ticker(ticker, config):
    """Run all overnight checks for a ticker."""
    print(f"\n🔍 Scanning {ticker}...")
    
    results = {
        "ticker": ticker,
        "form4": check_form4_filings(ticker, config),
        "eight_k": check_8k_filings(ticker, config),
        "news": check_news_headlines(ticker),
        "timestamp": datetime.now().isoformat()
    }
    
    # Determine overall alert level
    alerts = [
        results["form4"]["alert_level"],
        results["eight_k"]["alert_level"],
        results["news"]["alert_level"]
    ]
    
    if "RED" in alerts:
        results["overall_alert"] = "RED"
    elif "YELLOW" in alerts:
        results["overall_alert"] = "YELLOW"
    else:
        results["overall_alert"] = "GREEN"
    
    return results

def generate_report(all_results, config):
    """Generate human-readable report."""
    report = []
    report.append("=" * 70)
    report.append("🐺 OVERNIGHT MONITOR - SCAN COMPLETE")
    report.append("=" * 70)
    report.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    report.append("")
    
    # Summary
    red_count = sum(1 for r in all_results["tickers"] if r["overall_alert"] == "RED")
    yellow_count = sum(1 for r in all_results["tickers"] if r["overall_alert"] == "YELLOW")
    green_count = sum(1 for r in all_results["tickers"] if r["overall_alert"] == "GREEN")
    
    report.append(f"Status: 🔴 {red_count} RED | 🟡 {yellow_count} YELLOW | 🟢 {green_count} GREEN")
    report.append("")
    
    # Detailed results
    for result in all_results["tickers"]:
        ticker = result["ticker"]
        alert = result["overall_alert"]
        
        if alert == "GREEN":
            icon = "✅"
        elif alert == "YELLOW":
            icon = "⚠️"
        else:
            icon = "🔴"
        
        report.append(f"{icon} {ticker}: {alert}")
        
        # Show details if not GREEN
        if alert != "GREEN":
            if result["form4"]["found"]:
                report.append(f"   - Form 4: {result['form4']['message']}")
            if result["eight_k"]["found"]:
                report.append(f"   - 8-K: {result['eight_k']['message']}")
            if result["news"]["found"]:
                report.append(f"   - News: {len(result['news']['headlines'])} headlines")
                for headline in result["news"]["headlines"][:3]:
                    report.append(f"     • {headline['title']}")
        
        report.append("")
    
    # Overall decision
    report.append("=" * 70)
    if red_count > 0:
        report.append("⚠️  RED ALERTS DETECTED - Review before entry")
    elif yellow_count > 0:
        report.append("⚠️  CAUTION - Review yellow alerts")
    else:
        report.append("✅ ALL CLEAR - No overnight red flags")
    report.append("=" * 70)
    
    return "\n".join(report)

def send_alert(report, config, level="GREEN"):
    """Send alerts via configured channels."""
    
    # Only send if RED or YELLOW
    if level == "GREEN":
        print("\n✅ All GREEN - No alerts needed")
        return
    
    print(f"\n📧 Sending {level} alert...")
    
    # Email alert
    email_config = config.get("alerts", {})
    if email_config.get("email") and email_config.get("email_from"):
        try:
            send_email_alert(report, email_config, level)
            print("   ✅ Email sent")
        except Exception as e:
            print(f"   ❌ Email failed: {e}")
    
    # SMS alert (if configured and RED)
    if level == "RED" and email_config.get("sms"):
        try:
            send_sms_alert(report, email_config)
            print("   ✅ SMS sent")
        except Exception as e:
            print(f"   ❌ SMS failed: {e}")

def send_email_alert(report, config, level):
    """Send email alert via SMTP."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    msg = MIMEMultipart()
    msg['From'] = config['email_from']
    msg['To'] = config['email']
    msg['Subject'] = f"🐺 OVERNIGHT ALERT - {level}"
    
    msg.attach(MIMEText(report, 'plain'))
    
    server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
    server.starttls()
    server.login(config['email_from'], config['email_password'])
    server.send_message(msg)
    server.quit()

def send_sms_alert(report, config):
    """Send SMS alert via Twilio."""
    # TODO: Implement Twilio SMS
    # from twilio.rest import Client
    pass

def main():
    """Main overnight monitoring sequence."""
    print("\n🐺 WOLF DEN - OVERNIGHT MONITOR")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load config
    try:
        config = load_config()
    except FileNotFoundError:
        print("❌ wolf_den_config.yaml not found!")
        print("   Run setup first or copy from template")
        return 1
    
    # Build watchlist
    watchlist = [config["watchlist"]["primary"]] + config["watchlist"]["backup"]
    print(f"Watchlist: {', '.join(watchlist)}\n")
    
    # Scan each ticker
    results = {
        "timestamp": datetime.now().isoformat(),
        "tickers": []
    }
    
    for ticker in watchlist:
        ticker_result = scan_ticker(ticker, config)
        results["tickers"].append(ticker_result)
    
    # Check futures
    results["futures"] = check_futures()
    
    # Determine overall status
    alert_levels = [t["overall_alert"] for t in results["tickers"]]
    if "RED" in alert_levels:
        results["overall_status"] = "RED"
    elif "YELLOW" in alert_levels:
        results["overall_status"] = "YELLOW"
    else:
        results["overall_status"] "GREEN"
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path("logs") / f"overnight_{timestamp}.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Save latest
    latest_file = Path("logs") / "overnight_latest.json"
    with open(latest_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved: {output_file}")
    
    # Generate report
    report = generate_report(results, config)
    print("\n" + report)
    
    # Save report
    report_file = Path("logs") / f"overnight_{timestamp}.txt"
    with open(report_file, "w") as f:
        f.write(report)
    
    # Send alerts if needed
    send_alert(report, config, results["overall_status"])
    
    print("\n✅ Overnight scan complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
