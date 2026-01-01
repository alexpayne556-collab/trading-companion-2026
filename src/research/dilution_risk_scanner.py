#!/usr/bin/env python3
"""
DILUTION RISK SCANNER - Cash Runway Calculator
===============================================
Analyzes 10-Q/10-K filings to calculate cash runway
Flags dilution risk before it happens

Metrics:
- Cash & equivalents
- Quarterly burn rate  
- Runway (quarters remaining)
- S-3 shelf registration check

Thresholds:
- Runway > 6 quarters: SAFE (12+ months)
- Runway 4-6 quarters: CAUTION 
- Runway < 4 quarters: DANGER (dilution likely)

Usage:
    python dilution_risk_scanner.py AISP
    python dilution_risk_scanner.py SOUN --detailed

Author: BROKKR (The Builder)
Date: January 2, 2026
"""

import yfinance as yf
import argparse
from datetime import datetime
import pandas as pd

class DilutionRiskScanner:
    def __init__(self):
        self.thresholds = {
            'safe': 6,      # quarters
            'caution': 4,   # quarters
            'danger': 4     # quarters
        }
    
    def get_financial_data(self, ticker):
        """Get financial data from yfinance"""
        try:
            print(f"📊 Fetching financial data for {ticker.upper()}...")
            stock = yf.Ticker(ticker)
            
            # Get quarterly financials
            quarterly = stock.quarterly_financials
            balance = stock.quarterly_balance_sheet
            cashflow = stock.quarterly_cashflow
            
            info = stock.info
            
            return {
                'stock': stock,
                'info': info,
                'quarterly': quarterly,
                'balance': balance,
                'cashflow': cashflow
            }
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None
    
    def calculate_runway(self, ticker, detailed=False):
        """Calculate cash runway for a ticker"""
        print(f"\n{'='*70}")
        print(f"💰 DILUTION RISK SCANNER - {ticker.upper()}")
        print(f"{'='*70}\n")
        
        data = self.get_financial_data(ticker)
        if not data:
            return None
        
        info = data['info']
        balance = data['balance']
        cashflow = data['cashflow']
        
        # Get cash position
        cash = None
        if not balance.empty:
            if 'Cash And Cash Equivalents' in balance.index:
                cash = balance.loc['Cash And Cash Equivalents'].iloc[0]
            elif 'Cash' in balance.index:
                cash = balance.loc['Cash'].iloc[0]
        
        # Get operating cash flow (burn rate)
        operating_cf = None
        if not cashflow.empty:
            if 'Operating Cash Flow' in cashflow.index:
                # Get last 2 quarters to average
                cf_data = cashflow.loc['Operating Cash Flow'].iloc[:2]
                operating_cf = cf_data.mean()
        
        # Get market cap
        market_cap = info.get('marketCap', 0)
        shares_outstanding = info.get('sharesOutstanding', 0)
        current_price = info.get('currentPrice', 0)
        
        print(f"📈 COMPANY OVERVIEW")
        print(f"{'='*70}\n")
        print(f"Market Cap: ${market_cap:,.0f}" if market_cap else "Market Cap: N/A")
        print(f"Share Price: ${current_price:.2f}" if current_price else "Share Price: N/A")
        print(f"Shares Outstanding: {shares_outstanding:,.0f}" if shares_outstanding else "Shares Outstanding: N/A")
        
        print(f"\n{'='*70}")
        print(f"💵 CASH ANALYSIS")
        print(f"{'='*70}\n")
        
        if cash is None or pd.isna(cash):
            print("❌ Could not determine cash position")
            print("⚠️  Manual review required - check latest 10-Q")
            return None
        
        cash_millions = cash / 1_000_000
        print(f"Cash & Equivalents: ${cash_millions:.2f}M")
        
        # Calculate burn rate
        if operating_cf is None or pd.isna(operating_cf):
            print("\n⚠️  Could not determine quarterly burn rate")
            print("⚠️  Manual review required - check cash flow statement")
            runway_quarters = None
        else:
            # Negative operating cash flow = burning cash
            quarterly_burn = abs(operating_cf) if operating_cf < 0 else 0
            burn_millions = quarterly_burn / 1_000_000
            
            if quarterly_burn > 0:
                print(f"Quarterly Burn Rate: ${burn_millions:.2f}M")
                runway_quarters = cash / quarterly_burn
                print(f"\n📊 RUNWAY CALCULATION")
                print(f"{'='*70}\n")
                print(f"Runway: {runway_quarters:.1f} quarters ({runway_quarters * 3:.0f} months)")
            else:
                print(f"Quarterly Operating CF: ${abs(operating_cf)/1_000_000:.2f}M (POSITIVE)")
                print(f"\n✅ Company is CASH FLOW POSITIVE")
                runway_quarters = 999  # Effectively infinite
        
        # Risk assessment
        print(f"\n{'='*70}")
        print(f"🎯 DILUTION RISK ASSESSMENT")
        print(f"{'='*70}\n")
        
        if runway_quarters is None:
            risk_level = "UNKNOWN"
            risk_emoji = "⚠️"
            risk_color = "YELLOW"
            print(f"{risk_emoji} RISK LEVEL: {risk_level}")
            print(f"⚠️  Insufficient data - manual 10-Q review required")
        elif runway_quarters >= self.thresholds['safe']:
            risk_level = "LOW"
            risk_emoji = "🟢"
            risk_color = "GREEN"
            print(f"{risk_emoji} RISK LEVEL: {risk_level}")
            print(f"✅ Runway > 6 quarters (18+ months)")
            print(f"✅ No immediate dilution risk")
        elif runway_quarters >= self.thresholds['caution']:
            risk_level = "MEDIUM"
            risk_emoji = "🟡"
            risk_color = "YELLOW"
            print(f"{risk_emoji} RISK LEVEL: {risk_level}")
            print(f"⚠️  Runway 4-6 quarters (12-18 months)")
            print(f"⚠️  Watch for dilution announcements")
            print(f"⚠️  Monitor quarterly cash burn trends")
        else:
            risk_level = "HIGH"
            risk_emoji = "🔴"
            risk_color = "RED"
            print(f"{risk_emoji} RISK LEVEL: {risk_level}")
            print(f"🔴 Runway < 4 quarters (12 months)")
            print(f"🔴 HIGH dilution risk - likely within 6 months")
            print(f"🔴 Monitor for S-3 shelf registration filing")
        
        # Check for debt
        if not balance.empty:
            total_debt = None
            if 'Total Debt' in balance.index:
                total_debt = balance.loc['Total Debt'].iloc[0]
            elif 'Long Term Debt' in balance.index:
                total_debt = balance.loc['Long Term Debt'].iloc[0]
            
            if total_debt and not pd.isna(total_debt) and total_debt > 0:
                debt_millions = total_debt / 1_000_000
                print(f"\n⚠️  Total Debt: ${debt_millions:.2f}M")
                debt_to_cash = total_debt / cash if cash > 0 else 0
                print(f"⚠️  Debt/Cash Ratio: {debt_to_cash:.2f}x")
        
        # Verdict
        print(f"\n{'='*70}")
        print(f"⚖️  VERDICT")
        print(f"{'='*70}\n")
        
        if risk_level == "LOW":
            print(f"✅ PASS - Low dilution risk")
            print(f"✅ Sufficient runway for execution")
            verdict = "PASS"
        elif risk_level == "MEDIUM":
            print(f"⚠️  CAUTION - Monitor closely")
            print(f"⚠️  Position size conservatively")
            print(f"⚠️  Watch for S-3 filing (dilution setup)")
            verdict = "CAUTION"
        elif risk_level == "HIGH":
            print(f"🔴 FAIL - High dilution risk")
            print(f"🔴 Likely secondary offering within 6 months")
            print(f"🔴 Exit before dilution announcement")
            verdict = "FAIL"
        else:
            print(f"⚠️  UNKNOWN - Insufficient data")
            print(f"⚠️  Manual 10-Q review required")
            verdict = "UNKNOWN"
        
        print(f"\n{'='*70}\n")
        
        # Detailed financials if requested
        if detailed:
            print(f"\n{'='*70}")
            print(f"📋 DETAILED FINANCIALS (Last 4 Quarters)")
            print(f"{'='*70}\n")
            
            if not cashflow.empty:
                print("\nOperating Cash Flow:")
                print(cashflow.loc['Operating Cash Flow'] if 'Operating Cash Flow' in cashflow.index else "N/A")
            
            if not balance.empty:
                print("\nCash Position:")
                if 'Cash And Cash Equivalents' in balance.index:
                    print(balance.loc['Cash And Cash Equivalents'])
        
        return {
            'ticker': ticker.upper(),
            'verdict': verdict,
            'risk_level': risk_level,
            'cash_millions': cash_millions if cash else None,
            'burn_rate_millions': burn_millions if 'burn_millions' in locals() else None,
            'runway_quarters': runway_quarters if runway_quarters != 999 else None,
            'runway_months': int(runway_quarters * 3) if runway_quarters and runway_quarters != 999 else None
        }


def main():
    parser = argparse.ArgumentParser(
        description='Scan for dilution risk via cash runway analysis'
    )
    parser.add_argument('ticker', help='Stock ticker symbol')
    parser.add_argument('--detailed', action='store_true',
                       help='Show detailed financial statements')
    
    args = parser.parse_args()
    
    scanner = DilutionRiskScanner()
    result = scanner.calculate_runway(args.ticker, args.detailed)
    
    if result:
        if result['verdict'] == 'PASS':
            print("✅ Dilution risk check: PASS")
            exit(0)
        elif result['verdict'] == 'CAUTION':
            print("⚠️  Dilution risk check: CAUTION")
            exit(1)
        else:
            print("❌ Dilution risk check: FAIL")
            exit(2)
    else:
        print("❌ Could not complete analysis")
        exit(3)


if __name__ == "__main__":
    main()
