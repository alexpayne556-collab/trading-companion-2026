#!/usr/bin/env python3
"""
FORM 4 VALIDATOR - Transaction Code Checker
============================================
Scrapes SEC Form 4 filings to validate insider transaction codes
Distinguishes REAL conviction (Code P) from compensation (Code M/A)

Transaction Codes:
- P = Open market PURCHASE (REAL conviction - GREEN LIGHT)
- M = Option EXERCISE (compensation, NOT conviction - YELLOW)
- A = Award/GRANT (compensation - YELLOW)
- S = SALE (bearish - RED FLAG)

Usage:
    python form4_validator.py AISP
    python form4_validator.py AISP --recent 90  # Last 90 days only

Author: BROKKR (The Builder)
Date: January 2, 2026
"""

import requests
import argparse
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
import time

class Form4Validator:
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'Trading Companion research@example.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        
    def get_cik(self, ticker):
        """Get CIK number for ticker from SEC"""
        try:
            # Try SEC company tickers JSON
            url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            companies = response.json()
            ticker_upper = ticker.upper()
            
            for company in companies.values():
                if company['ticker'] == ticker_upper:
                    cik = str(company['cik_str']).zfill(10)
                    print(f"✅ Found CIK for {ticker}: {cik}")
                    return cik
                    
            print(f"❌ Could not find CIK for {ticker}")
            return None
            
        except Exception as e:
            print(f"❌ Error getting CIK: {e}")
            return None
    
    def get_form4_filings(self, cik, days_back=365):
        """Get recent Form 4 filings for a CIK"""
        try:
            # SEC EDGAR search for Form 4
            url = f"{self.base_url}/cgi-bin/browse-edgar"
            params = {
                'action': 'getcompany',
                'CIK': cik,
                'type': '4',
                'dateb': '',
                'owner': 'include',
                'count': '100'
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            time.sleep(0.2)  # Rate limiting
            
            soup = BeautifulSoup(response.content, 'html.parser')
            filings = []
            
            # Find all Form 4 filing rows
            table = soup.find('table', {'class': 'tableFile2'})
            if not table:
                print(f"⚠️  No Form 4 filings found")
                return []
            
            rows = table.find_all('tr')[1:]  # Skip header
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4:
                    continue
                    
                # Get filing date
                date_str = cols[3].text.strip()
                filing_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if filing_date < cutoff_date:
                    continue
                
                # Get document link
                doc_link = cols[1].find('a', {'id': 'documentsbutton'})
                if doc_link:
                    doc_url = self.base_url + doc_link['href']
                    filings.append({
                        'date': date_str,
                        'url': doc_url,
                        'filing_date': filing_date
                    })
            
            print(f"✅ Found {len(filings)} Form 4 filings in last {days_back} days")
            return filings
            
        except Exception as e:
            print(f"❌ Error getting Form 4 filings: {e}")
            return []
    
    def parse_form4_transactions(self, filing_url):
        """Parse Form 4 to extract transaction details"""
        try:
            response = requests.get(filing_url, headers=self.headers)
            response.raise_for_status()
            time.sleep(0.2)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the actual Form 4 XML document
            xml_link = None
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if 'primary_doc.xml' in href.lower() or href.endswith('.xml'):
                    xml_link = self.base_url + href if not href.startswith('http') else href
                    break
            
            if not xml_link:
                # Try to find first XML document
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    if '.xml' in href.lower():
                        xml_link = self.base_url + href if not href.startswith('http') else href
                        break
            
            if not xml_link:
                return []
            
            # Get and parse the XML
            xml_response = requests.get(xml_link, headers=self.headers)
            xml_response.raise_for_status()
            time.sleep(0.2)
            
            xml_soup = BeautifulSoup(xml_response.content, 'xml')
            
            transactions = []
            
            # Get reporting owner info
            owner_name = "Unknown"
            owner_title = "Unknown"
            
            reporting_owner = xml_soup.find('reportingOwner')
            if reporting_owner:
                name_tag = reporting_owner.find('rptOwnerName')
                if name_tag:
                    owner_name = name_tag.text.strip()
                    
                title_tag = reporting_owner.find('officerTitle')
                if title_tag:
                    owner_title = title_tag.text.strip()
                else:
                    # Check if director
                    is_director = reporting_owner.find('isDirector')
                    if is_director and is_director.text.strip() == '1':
                        owner_title = "Director"
            
            # Parse non-derivative transactions
            for transaction in xml_soup.find_all('nonDerivativeTransaction'):
                trans_code = transaction.find('transactionCode')
                trans_date = transaction.find('transactionDate')
                trans_shares = transaction.find('transactionShares')
                trans_price = transaction.find('transactionPricePerShare')
                
                if trans_code and trans_date and trans_shares:
                    code = trans_code.find('value')
                    code_text = code.text.strip() if code else "?"
                    
                    shares = trans_shares.find('value')
                    shares_num = float(shares.text.strip()) if shares else 0
                    
                    price = "N/A"
                    value = 0
                    if trans_price:
                        price_val = trans_price.find('value')
                        if price_val:
                            try:
                                price_num = float(price_val.text.strip())
                                price = f"${price_num:.2f}"
                                value = shares_num * price_num
                            except:
                                pass
                    
                    transactions.append({
                        'name': owner_name,
                        'title': owner_title,
                        'code': code_text,
                        'date': trans_date.find('value').text.strip() if trans_date.find('value') else "?",
                        'shares': int(shares_num),
                        'price': price,
                        'value': value
                    })
            
            # Parse derivative transactions (options)
            for transaction in xml_soup.find_all('derivativeTransaction'):
                trans_code = transaction.find('transactionCode')
                trans_date = transaction.find('transactionDate')
                trans_shares = transaction.find('transactionShares')
                
                if trans_code and trans_date and trans_shares:
                    code = trans_code.find('value')
                    code_text = code.text.strip() if code else "?"
                    
                    shares = trans_shares.find('value')
                    shares_num = float(shares.text.strip()) if shares else 0
                    
                    transactions.append({
                        'name': owner_name,
                        'title': owner_title,
                        'code': code_text,
                        'date': trans_date.find('value').text.strip() if trans_date.find('value') else "?",
                        'shares': int(shares_num),
                        'price': "OPTION",
                        'value': 0
                    })
            
            return transactions
            
        except Exception as e:
            print(f"⚠️  Could not parse Form 4: {e}")
            return []
    
    def validate_ticker(self, ticker, days_back=365):
        """Full validation of insider transactions for a ticker"""
        print(f"\n{'='*70}")
        print(f"🔍 FORM 4 VALIDATOR - {ticker.upper()}")
        print(f"{'='*70}\n")
        
        # Get CIK
        cik = self.get_cik(ticker)
        if not cik:
            return None
        
        # Get Form 4 filings
        filings = self.get_form4_filings(cik, days_back)
        if not filings:
            print(f"⚠️  No Form 4 filings found in last {days_back} days")
            return None
        
        # Parse all transactions
        all_transactions = []
        print(f"\n📄 Parsing {len(filings)} Form 4 filings...\n")
        
        for i, filing in enumerate(filings[:20]):  # Limit to 20 most recent
            print(f"   Processing filing {i+1}/{min(len(filings), 20)}...", end='\r')
            transactions = self.parse_form4_transactions(filing['url'])
            for trans in transactions:
                trans['filing_date'] = filing['date']
                all_transactions.append(trans)
        
        print(f"\n✅ Parsed {len(all_transactions)} total transactions\n")
        
        # Analyze transaction codes
        code_counts = {}
        conviction_buys = []
        compensation_actions = []
        sales = []
        
        for trans in all_transactions:
            code = trans['code']
            code_counts[code] = code_counts.get(code, 0) + 1
            
            if code == 'P':
                conviction_buys.append(trans)
            elif code in ['M', 'A']:
                compensation_actions.append(trans)
            elif code == 'S':
                sales.append(trans)
        
        # Print results
        print(f"{'='*70}")
        print(f"📊 TRANSACTION CODE ANALYSIS")
        print(f"{'='*70}\n")
        
        print("Transaction Code Breakdown:")
        for code, count in sorted(code_counts.items()):
            code_desc = {
                'P': 'Open Market PURCHASE (CONVICTION)',
                'M': 'Option EXERCISE (compensation)',
                'A': 'Award/GRANT (compensation)',
                'S': 'SALE (bearish)',
                'C': 'Conversion',
                'D': 'Disposition',
                'F': 'Tax withholding',
                'G': 'Gift',
                'I': 'Discretionary transaction'
            }.get(code, 'Other')
            
            emoji = {
                'P': '🟢',
                'M': '🟡',
                'A': '🟡',
                'S': '🔴'
            }.get(code, '⚪')
            
            print(f"  {emoji} Code {code}: {count:3d} transactions - {code_desc}")
        
        # CONVICTION BUYS (Code P)
        if conviction_buys:
            print(f"\n{'='*70}")
            print(f"🟢 CONVICTION BUYS (Code P = Open Market Purchase)")
            print(f"{'='*70}\n")
            
            total_conviction_value = 0
            
            for trans in conviction_buys:
                print(f"📅 {trans['date']} | {trans['name']}")
                print(f"   Title: {trans['title']}")
                print(f"   Shares: {trans['shares']:,} @ {trans['price']}")
                if trans['value'] > 0:
                    print(f"   💰 Value: ${trans['value']:,.0f}")
                    total_conviction_value += trans['value']
                print()
            
            print(f"✅ TOTAL CONVICTION BUYING: ${total_conviction_value:,.0f}")
            print(f"✅ {len(conviction_buys)} insider(s) buying with REAL money (Code P)")
            
        else:
            print(f"\n{'='*70}")
            print(f"❌ NO CONVICTION BUYS (Code P)")
            print(f"{'='*70}\n")
            print("⚠️  All insider activity is compensation-based (codes M/A/F)")
            print("⚠️  NO insiders buying with their own money on open market")
            print("🔴 RED FLAG: Lack of insider conviction")
        
        # COMPENSATION ACTIONS
        if compensation_actions:
            print(f"\n{'='*70}")
            print(f"🟡 COMPENSATION ACTIONS (Codes M/A - NOT conviction)")
            print(f"{'='*70}\n")
            print(f"Found {len(compensation_actions)} compensation-based transactions")
            print("(These are option exercises/grants, NOT open market purchases)\n")
        
        # SALES
        if sales:
            print(f"\n{'='*70}")
            print(f"🔴 INSIDER SALES (Code S)")
            print(f"{'='*70}\n")
            
            total_sales_value = 0
            for trans in sales:
                if trans['value'] > 0:
                    total_sales_value += trans['value']
            
            print(f"⚠️  {len(sales)} insider sale(s)")
            if total_sales_value > 0:
                print(f"⚠️  Total sold: ${total_sales_value:,.0f}")
        
        # FINAL VERDICT
        print(f"\n{'='*70}")
        print(f"🎯 VERDICT")
        print(f"{'='*70}\n")
        
        if conviction_buys:
            conviction_score = min(100, len(conviction_buys) * 30)
            print(f"✅ PASS - Insiders buying with REAL money (Code P)")
            print(f"✅ {len(conviction_buys)} conviction buy(s) totaling ${total_conviction_value:,.0f}")
            print(f"📊 Conviction Score: {conviction_score}/100")
            verdict = "GREEN_LIGHT"
        else:
            print(f"❌ FAIL - NO open market purchases (Code P)")
            print(f"⚠️  Only compensation-based activity (codes M/A/F)")
            print(f"🔴 This is NOT insider conviction")
            print(f"📊 Conviction Score: 0/100")
            verdict = "RED_FLAG"
        
        print(f"\n{'='*70}\n")
        
        return {
            'ticker': ticker.upper(),
            'verdict': verdict,
            'conviction_buys': len(conviction_buys),
            'conviction_value': total_conviction_value if conviction_buys else 0,
            'compensation_actions': len(compensation_actions),
            'sales': len(sales),
            'transactions': all_transactions
        }


def main():
    parser = argparse.ArgumentParser(
        description='Validate insider Form 4 transaction codes'
    )
    parser.add_argument('ticker', help='Stock ticker symbol')
    parser.add_argument('--recent', type=int, default=365, 
                       help='Days back to search (default: 365)')
    
    args = parser.parse_args()
    
    validator = Form4Validator()
    result = validator.validate_ticker(args.ticker, args.recent)
    
    if result:
        if result['verdict'] == 'GREEN_LIGHT':
            print("✅ Form 4 validation: PASS")
            exit(0)
        else:
            print("❌ Form 4 validation: FAIL")
            exit(1)
    else:
        print("❌ Could not complete validation")
        exit(2)


if __name__ == "__main__":
    main()
