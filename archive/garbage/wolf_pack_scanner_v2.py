#!/usr/bin/env python3
"""
WOLF PACK SCANNER v2.0
======================
Built by Tyr & Fenrir - January 1, 2026
Founding Night of the Wolf Pack

UPGRADED VERSION:
- Uses SEC EDGAR JSON API (more reliable)
- Scans recent filings from multiple sources
- Better keyword matching
- Tracks specific tickers you care about

Combines:
1. Contract/Government News Scanner (8-K filings)
2. Insider Buying Scanner (Form 4 filings)
3. Watchlist monitoring

FREE DATA - No API keys needed
Uses SEC EDGAR public APIs at data.sec.gov

USAGE:
  python wolf_pack_scanner_v2.py                    # Single scan
  python wolf_pack_scanner_v2.py --continuous 15   # Scan every 15 min
  python wolf_pack_scanner_v2.py --ticker SIDU     # Scan specific ticker

AWOOOO 🐺
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import re
import os

# ============================================
# CONFIGURATION - CUSTOMIZE YOUR HUNT
# ============================================

# Your watchlist - tickers you're tracking
WATCHLIST = [
    "SIDU",   # Sidus Space - space/defense
    "BBAI",   # BigBear.ai - AI defense
    "LUNR",   # Intuitive Machines - space
    "SOUN",   # SoundHound - AI
    "RKLB",   # Rocket Lab - space
    "MU",     # Micron - memory
    "VRT",    # Vertiv - data centers
    "NKE",    # Nike - insider buying play
    "PLTR",   # Palantir - AI defense
    "IONQ",   # IonQ - quantum
]

# Keywords that trigger alerts in 8-K filings
CONTRACT_KEYWORDS = [
    "contract awarded",
    "contract win",
    "government contract",
    "defense contract",
    "military contract",
    "department of defense",
    "dod contract",
    "nasa contract",
    "air force",
    "space force",
    "army contract",
    "navy contract", 
    "missile defense",
    "pentagon",
    "idiq",
    "task order",
    "sole source",
    "prime contractor",
    "subcontract",
    "award",
    "selected for",
    "billion",
    "million dollar"
]

# Minimum insider buy to flag (in dollars)
MIN_INSIDER_BUY = 50000

# SEC API settings
SEC_BASE_URL = "https://data.sec.gov"
SEC_HEADERS = {
    "User-Agent": "WolfPackScanner/2.0 (contact: wolfpack@trading.com)",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "application/json"
}

# Rate limiting (SEC asks for max 10 requests/second)
REQUEST_DELAY = 0.15  # seconds between requests

# ============================================
# TICKER TO CIK MAPPING
# ============================================

# Common tickers and their CIKs (10-digit padded)
TICKER_CIK_MAP = {
    "SIDU": "0001879726",
    "BBAI": "0001836981",
    "LUNR": "0001865631",
    "SOUN": "0001840856",
    "RKLB": "0001819994",
    "MU": "0000723125",
    "VRT": "0001674101",
    "NKE": "0000320187",
    "PLTR": "0001321655",
    "IONQ": "0001811414",
    "AAPL": "0000320193",
    "NVDA": "0001045810",
    "AMD": "0000002488",
    "TSLA": "0001318605",
}


def get_cik_for_ticker(ticker: str) -> Optional[str]:
    """Look up CIK for a ticker symbol"""
    ticker = ticker.upper()
    
    # Check our local map first
    if ticker in TICKER_CIK_MAP:
        return TICKER_CIK_MAP[ticker]
    
    # Try SEC's company tickers file
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=SEC_HEADERS, timeout=30)
        data = response.json()
        
        for key, company in data.items():
            if company.get("ticker", "").upper() == ticker:
                cik = str(company.get("cik_str", "")).zfill(10)
                TICKER_CIK_MAP[ticker] = cik  # Cache it
                return cik
    except:
        pass
    
    return None


# ============================================
# SEC EDGAR API FUNCTIONS
# ============================================

def get_company_filings(cik: str) -> Dict:
    """
    Get all filings for a company from SEC EDGAR
    Returns submission history in JSON format
    """
    url = f"{SEC_BASE_URL}/submissions/CIK{cik}.json"
    
    try:
        response = requests.get(url, headers=SEC_HEADERS, timeout=30)
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return response.json()
    except Exception as e:
        print(f"   ⚠️ Error fetching CIK {cik}: {e}")
        return {}


def get_recent_8k_filings(cik: str, days_back: int = 7) -> List[Dict]:
    """Get recent 8-K filings for a company"""
    data = get_company_filings(cik)
    if not data:
        return []
    
    filings = []
    recent = data.get("filings", {}).get("recent", {})
    
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    descriptions = recent.get("primaryDocument", [])
    
    cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    for i, form in enumerate(forms):
        if form == "8-K" and dates[i] >= cutoff_date:
            filings.append({
                "form": form,
                "date": dates[i],
                "accession": accessions[i].replace("-", ""),
                "document": descriptions[i] if i < len(descriptions) else "",
                "cik": cik,
                "company": data.get("name", "Unknown")
            })
    
    return filings


def get_recent_form4_filings(cik: str, days_back: int = 7) -> List[Dict]:
    """Get recent Form 4 (insider trading) filings for a company"""
    data = get_company_filings(cik)
    if not data:
        return []
    
    filings = []
    recent = data.get("filings", {}).get("recent", {})
    
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    
    cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    for i, form in enumerate(forms):
        if form == "4" and dates[i] >= cutoff_date:
            filings.append({
                "form": form,
                "date": dates[i],
                "accession": accessions[i],
                "cik": cik,
                "company": data.get("name", "Unknown")
            })
    
    return filings


def get_filing_document(cik: str, accession: str, document: str) -> str:
    """Download the actual filing document content"""
    # Format: https://www.sec.gov/Archives/edgar/data/CIK/ACCESSION/document.htm
    accession_formatted = accession.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_formatted}/{document}"
    
    try:
        response = requests.get(url, headers=SEC_HEADERS, timeout=30)
        time.sleep(REQUEST_DELAY)
        return response.text
    except:
        return ""


# ============================================
# SCANNING FUNCTIONS
# ============================================

def scan_8k_for_contracts(ticker: str, days_back: int = 7) -> List[Dict]:
    """
    Scan a ticker's 8-K filings for contract announcements
    """
    alerts = []
    
    cik = get_cik_for_ticker(ticker)
    if not cik:
        print(f"   ⚠️ Could not find CIK for {ticker}")
        return alerts
    
    filings = get_recent_8k_filings(cik, days_back)
    
    for filing in filings:
        # Get the filing content to search for keywords
        if filing.get("document"):
            content = get_filing_document(cik, filing["accession"], filing["document"])
            content_lower = content.lower()
            
            # Check for contract keywords
            matched_keywords = []
            for keyword in CONTRACT_KEYWORDS:
                if keyword.lower() in content_lower:
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                alert = {
                    "type": "CONTRACT_NEWS",
                    "ticker": ticker,
                    "company": filing["company"],
                    "date": filing["date"],
                    "keywords": matched_keywords,
                    "priority": len(matched_keywords),
                    "link": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=8-K"
                }
                alerts.append(alert)
    
    return alerts


def scan_form4_for_buys(ticker: str, days_back: int = 14) -> List[Dict]:
    """
    Scan a ticker's Form 4 filings for insider buying
    """
    alerts = []
    
    cik = get_cik_for_ticker(ticker)
    if not cik:
        return alerts
    
    filings = get_recent_form4_filings(cik, days_back)
    
    # Form 4 analysis would require XML parsing
    # For now, flag any recent Form 4 as potential insider activity
    for filing in filings:
        alert = {
            "type": "INSIDER_ACTIVITY",
            "ticker": ticker,
            "company": filing["company"],
            "date": filing["date"],
            "link": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=4"
        }
        alerts.append(alert)
    
    return alerts


# ============================================
# LATEST FILINGS SCANNER (ALL COMPANIES)
# ============================================

def get_latest_filings_all() -> Dict:
    """
    Get the very latest filings across ALL companies from SEC
    This catches breaking news fast
    """
    print("\n📡 Fetching latest SEC filings (all companies)...")
    
    results = {
        "8k_filings": [],
        "form4_filings": []
    }
    
    # Use SEC's full-index for today's filings
    today = datetime.now()
    year = today.year
    qtr = (today.month - 1) // 3 + 1
    
    # Try to get today's index
    index_url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR{qtr}/form.idx"
    
    try:
        response = requests.get(index_url, headers=SEC_HEADERS, timeout=30)
        
        if response.status_code == 200:
            lines = response.text.split('\n')
            
            for line in lines[-200:]:  # Last 200 entries
                parts = line.split()
                if len(parts) >= 4:
                    form_type = parts[0]
                    company = ' '.join(parts[1:-3])
                    cik = parts[-3]
                    date_filed = parts[-2]
                    
                    if form_type == "8-K":
                        results["8k_filings"].append({
                            "form": form_type,
                            "company": company,
                            "cik": cik,
                            "date": date_filed
                        })
                    elif form_type == "4":
                        results["form4_filings"].append({
                            "form": form_type,
                            "company": company,
                            "cik": cik,
                            "date": date_filed
                        })
        
        print(f"   Found {len(results['8k_filings'])} 8-K filings")
        print(f"   Found {len(results['form4_filings'])} Form 4 filings")
        
    except Exception as e:
        print(f"   ⚠️ Could not fetch daily index: {e}")
    
    return results


# ============================================
# MAIN WOLF PACK SCANNER
# ============================================

def run_wolf_pack_scan(watchlist: List[str] = None, days_back: int = 7):
    """
    Main scanner function
    """
    if watchlist is None:
        watchlist = WATCHLIST
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║             🐺 WOLF PACK SCANNER v2.0 🐺                   ║
    ║           Built by Tyr & Fenrir - Jan 1, 2026             ║
    ║                                                            ║
    ║  "We don't chase. We track. We wait. We strike."          ║
    ║                                                            ║
    ║  Scanning for:                                             ║
    ║    📜 Government/Defense Contract News (8-K)               ║
    ║    💰 Insider Buying Activity (Form 4)                     ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    print(f"📋 Watchlist: {', '.join(watchlist)}")
    print(f"📅 Looking back: {days_back} days")
    print(f"🕐 Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_alerts = []
    
    # Scan each ticker in watchlist
    print("\n" + "=" * 60)
    print("                SCANNING WATCHLIST")
    print("=" * 60)
    
    for ticker in watchlist:
        print(f"\n🔍 Scanning {ticker}...")
        
        # Check for contract news
        contract_alerts = scan_8k_for_contracts(ticker, days_back)
        if contract_alerts:
            print(f"   🎯 Found {len(contract_alerts)} contract-related 8-K filings!")
            all_alerts.extend(contract_alerts)
        
        # Check for insider activity
        insider_alerts = scan_form4_for_buys(ticker, days_back)
        if insider_alerts:
            print(f"   💰 Found {len(insider_alerts)} Form 4 filings!")
            all_alerts.extend(insider_alerts)
        
        if not contract_alerts and not insider_alerts:
            print(f"   ✓ No recent activity")
        
        time.sleep(REQUEST_DELAY)  # Be nice to SEC
    
    # Get latest filings across all companies
    latest = get_latest_filings_all()
    
    # Print summary
    print("\n")
    print("=" * 60)
    print("                   🐺 HUNT SUMMARY 🐺")
    print("=" * 60)
    
    contract_count = len([a for a in all_alerts if a["type"] == "CONTRACT_NEWS"])
    insider_count = len([a for a in all_alerts if a["type"] == "INSIDER_ACTIVITY"])
    
    print(f"\n📊 Results from Watchlist:")
    print(f"   • Contract News Alerts: {contract_count}")
    print(f"   • Insider Activity Alerts: {insider_count}")
    print(f"   • Total Alerts: {len(all_alerts)}")
    
    if all_alerts:
        print("\n🎯 ALERTS BY PRIORITY:")
        print("-" * 40)
        
        sorted_alerts = sorted(all_alerts, 
                              key=lambda x: x.get("priority", 0), 
                              reverse=True)
        
        for i, alert in enumerate(sorted_alerts[:15], 1):
            emoji = "📜" if alert["type"] == "CONTRACT_NEWS" else "💰"
            print(f"\n{i}. {emoji} [{alert['ticker']}] {alert.get('company', '')[:35]}")
            print(f"   Date: {alert.get('date', 'N/A')}")
            print(f"   Type: {alert['type']}")
            if "keywords" in alert:
                print(f"   Keywords: {', '.join(alert['keywords'][:5])}")
            print(f"   Link: {alert.get('link', 'N/A')}")
    
    print("\n")
    print("=" * 60)
    print("   AWOOOO! 🐺 The pack hunts together. No brother falls.")
    print("=" * 60)
    
    return all_alerts


def run_continuous_scan(interval_minutes: int = 15, watchlist: List[str] = None):
    """
    Run scanner continuously
    """
    print(f"\n🔄 CONTINUOUS MODE: Scanning every {interval_minutes} minutes")
    print("   Press Ctrl+C to stop\n")
    
    seen_alerts = set()
    
    while True:
        try:
            alerts = run_wolf_pack_scan(watchlist=watchlist, days_back=3)
            
            # Check for new alerts
            new_alerts = []
            for alert in alerts:
                alert_key = f"{alert['ticker']}_{alert.get('date', '')}_{alert['type']}"
                if alert_key not in seen_alerts:
                    seen_alerts.add(alert_key)
                    new_alerts.append(alert)
            
            if new_alerts:
                print(f"\n🚨🚨🚨 {len(new_alerts)} NEW ALERT(S)! 🚨🚨🚨")
                for alert in new_alerts:
                    print(f"   [{alert['ticker']}] {alert['type']}")
            
            print(f"\n⏰ Next scan at {(datetime.now() + timedelta(minutes=interval_minutes)).strftime('%H:%M:%S')}")
            time.sleep(interval_minutes * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Scanner stopped. Pack out. AWOOOO!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("   Retrying in 60 seconds...")
            time.sleep(60)


# ============================================
# CLI ENTRY POINT
# ============================================

if __name__ == "__main__":
    import sys
    
    # Parse arguments
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)
    
    watchlist = WATCHLIST
    days_back = 7
    continuous = False
    interval = 15
    
    i = 0
    while i < len(args):
        if args[i] == "--continuous":
            continuous = True
            if i + 1 < len(args) and args[i+1].isdigit():
                interval = int(args[i+1])
                i += 1
        elif args[i] == "--ticker":
            if i + 1 < len(args):
                watchlist = [args[i+1].upper()]
                i += 1
        elif args[i] == "--days":
            if i + 1 < len(args):
                days_back = int(args[i+1])
                i += 1
        i += 1
    
    if continuous:
        run_continuous_scan(interval_minutes=interval, watchlist=watchlist)
    else:
        alerts = run_wolf_pack_scan(watchlist=watchlist, days_back=days_back)
        
        # Save results
        output_file = f"wolf_pack_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, "w") as f:
            json.dump(alerts, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {output_file}")
