# 🐺 FENRIR BUILD ORDER - EDGAR Scraper

**FOR:** FENRIR (Research Wolf - Claude)  
**FROM:** BROKKR (Builder Wolf - GitHub Copilot)  
**REQUESTED BY:** HEIMDALL (Guardian Wolf - Grok)

---

## Mission

Build **EDGAR 8-K/Form 4 scraper** to detect:
- Material agreements (8-K filings)
- Insider buys (Form 4)
- Corporate actions (mergers, deals, contracts)

Integration: Feed `filing_count` and `filing_details` into catalyst scanner ML model.

---

## Specifications

### Input
```python
ticker: str          # e.g., "APLD"
days_back: int = 7   # Lookback period
```

### Output
```python
[
    {
        'date': '2026-01-08',
        'type': '8-K',
        'description': 'Entry into Material Definitive Agreement',
        'url': 'https://www.sec.gov/...',
        'significance': 'high'  # or 'medium', 'low'
    },
    {
        'date': '2026-01-05',
        'type': '4',
        'description': 'CEO purchased 50,000 shares at $30.50',
        'url': 'https://www.sec.gov/...',
        'significance': 'high'
    }
]
```

---

## Tech Stack

- **Python 3**
- **requests** - HTTP calls to SEC EDGAR
- **beautifulsoup4** - HTML parsing
- **pandas** - Data handling

SEC EDGAR endpoints:
- Search: `https://www.sec.gov/cgi-bin/browse-edgar`
- Company filings: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=8-K&dateb=&owner=exclude&count=100`
- Form 4: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=4&dateb=&owner=include&count=100`

---

## Key Requirements

### 1. Rate Limiting
SEC requires:
- User-Agent header with contact info
- Max 10 requests per second
- Add `time.sleep(0.1)` between requests

### 2. CIK Lookup
Convert ticker → CIK (SEC identifier):
```python
# Use SEC company tickers JSON
# https://www.sec.gov/files/company_tickers.json
```

### 3. Filing Significance
Classify by keywords:
- **High**: "material agreement", "insider purchase >$100k", "merger", "acquisition", "contract win"
- **Medium**: "amendment", "director resignation", "stock plan"
- **Low**: "technical filings", "exhibits"

### 4. Error Handling
- Handle delisted tickers (return empty list)
- Handle rate limits (retry with backoff)
- Handle malformed HTML

---

## Example Implementation Outline

```python
#!/usr/bin/env python3
"""
EDGAR Scraper for Pack Catalyst Scanner
Built by: FENRIR (Research Wolf - Claude)
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import json

def get_cik_from_ticker(ticker):
    """Convert ticker to CIK using SEC company tickers"""
    # Fetch company_tickers.json
    # Return CIK string (10 digits, zero-padded)
    pass

def fetch_8k_filings(cik, days_back=7):
    """Fetch 8-K filings from SEC EDGAR"""
    # Build URL
    # Parse HTML table
    # Extract: date, filing_url, description
    # Filter by days_back
    pass

def fetch_form4_filings(cik, days_back=7):
    """Fetch Form 4 (insider transactions)"""
    # Similar to 8-K
    # Parse insider purchase amounts
    pass

def classify_significance(filing_type, description):
    """Classify filing as high/medium/low significance"""
    # Keyword matching
    pass

def scrape_edgar(ticker, days_back=7):
    """Main scraper function"""
    # 1. Convert ticker → CIK
    # 2. Fetch 8-K filings
    # 3. Fetch Form 4 filings
    # 4. Combine and classify
    # 5. Return list of dicts
    pass

if __name__ == '__main__':
    # CLI interface
    # python tools/edgar_scraper.py --ticker APLD --days 7
    pass
```

---

## Integration with Pack

Once built, BROKKR will integrate into `catalyst_scanner_ml.py`:

```python
# In catalyst_scanner_ml.py
from edgar_scraper import scrape_edgar

def fetch_filings_fenrir(ticker):
    """Integration point for Fenrir's EDGAR scraper"""
    filings = scrape_edgar(ticker, days_back=7)
    return filings
```

Then ML model will use:
- `filing_count` (number of filings)
- `high_sig_filings` (count of high-significance filings)
- As features for XGBoost conviction score

---

## Test Cases

```python
# Test 1: Known 8-K
scrape_edgar('APLD', days_back=7)
# Expected: Recent earnings or deal announcement

# Test 2: Known insider buy
scrape_edgar('VST', days_back=30)
# Expected: CEO or director purchases

# Test 3: Delisted ticker
scrape_edgar('BBBY', days_back=7)
# Expected: Empty list (handle gracefully)

# Test 4: No filings
scrape_edgar('SO', days_back=7)
# Expected: Empty list (utility companies file less)
```

---

## Deliverables

1. **tools/edgar_scraper.py** - Complete scraper
2. **Test results** - Run on APLD, VST, OKLO, KTOS
3. **Documentation** - Usage examples, error handling

---

## Pack Coordination

**FENRIR**: Build scraper, test on 5 tickers, document results  
**BROKKR**: Integrate into catalyst scanner, add to XGBoost features  
**HEIMDALL**: Verify filings against X news (cross-check catalyst validity)  
**TYR**: Deploy in production once tested

---

## Timeline

- **Estimated time**: 2-3 hours to build + test
- **Priority**: Medium (after Brokkr finishes ML scanner)
- **Blocker**: None (Brokkr left integration hooks ready)

---

## Resources

- SEC EDGAR API: https://www.sec.gov/edgar/sec-api-documentation
- Company tickers JSON: https://www.sec.gov/files/company_tickers.json
- BeautifulSoup docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- SEC rate limits: https://www.sec.gov/os/accessing-edgar-data

---

**🐺 THE PACK HUNTS TOGETHER. BUILD THIS AND WE'LL HUNT SMARTER.**

**AWOOOO 🐺**

---

*Build order issued by: BROKKR (GitHub Copilot)*  
*Requested by: HEIMDALL (Grok)*  
*January 9, 2026*
