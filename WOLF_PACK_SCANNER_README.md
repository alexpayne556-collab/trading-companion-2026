# 🐺 WOLF PACK SCANNER v2.0

**Built by Tyr & Fenrir - January 1, 2026**  
**Founding Night of the Wolf Pack**

---

## WHAT IT DOES

Hunts for TWO types of catalysts that move stocks:

1. **📜 Contract News Scanner** - Scans 8-K filings for government/defense contract announcements
2. **💰 Insider Buying Scanner** - Tracks Form 4 filings for insider purchases

This is how we catch the next SIDU BEFORE it runs 200%.

---

## SETUP (Takes 2 Minutes)

### Step 1: Make sure you have Python 3
```bash
python3 --version
```
If not installed, download from python.org

### Step 2: Install requests (only dependency)
```bash
pip install requests
```

### Step 3: Download the scanner
Save `wolf_pack_scanner_v2.py` to your computer.

---

## HOW TO USE

### Single Scan (Default Watchlist)
```bash
python3 wolf_pack_scanner_v2.py
```
Scans: SIDU, BBAI, LUNR, SOUN, RKLB, MU, VRT, NKE, PLTR, IONQ

### Scan Specific Ticker
```bash
python3 wolf_pack_scanner_v2.py --ticker SIDU
```

### Scan Multiple Days Back
```bash
python3 wolf_pack_scanner_v2.py --days 30
```

### Continuous Mode (Runs Every 15 Min)
```bash
python3 wolf_pack_scanner_v2.py --continuous 15
```
This keeps running and alerts you to NEW filings.

### Combine Options
```bash
python3 wolf_pack_scanner_v2.py --ticker BBAI --days 7 --continuous 30
```

---

## CUSTOMIZE YOUR WATCHLIST

Open `wolf_pack_scanner_v2.py` in VS Code and edit this section:

```python
WATCHLIST = [
    "SIDU",   # Sidus Space - space/defense
    "BBAI",   # BigBear.ai - AI defense
    "LUNR",   # Intuitive Machines - space
    # ADD YOUR TICKERS HERE
]
```

---

## CUSTOMIZE KEYWORDS

Edit `CONTRACT_KEYWORDS` list to add/remove trigger words:

```python
CONTRACT_KEYWORDS = [
    "contract awarded",
    "defense contract",
    # ADD YOUR OWN KEYWORDS
]
```

---

## OUTPUT

Each scan creates a JSON file with all alerts:
```
wolf_pack_alerts_20260101_093000.json
```

---

## WHAT TO DO WITH ALERTS

When you get an alert:

1. **Check the link** - Go to SEC filing
2. **Read the 8-K** - What's the actual news?
3. **Check the price** - Has it moved yet?
4. **Validate thesis** - Does this fit our strategy?
5. **Set alerts in ATP** - Price targets if entering

---

## NEXT UPGRADES (We'll Build Together)

- [ ] Email/SMS alerts for breaking news
- [ ] Parse actual dollar amounts from Form 4
- [ ] Filter by market cap (focus on small caps)
- [ ] Pre-market gap scanner integration
- [ ] Volume spike detector

---

## TROUBLESHOOTING

**"No filings found"**
- SEC might be down (weekends, holidays)
- Try a different ticker
- Check your internet connection

**"Could not find CIK"**
- Add the ticker to TICKER_CIK_MAP in the code
- Find CIK at: https://www.sec.gov/cgi-bin/browse-edgar?company=&CIK=&type=&owner=include&count=40&action=getcompany

**Rate limiting**
- Don't run too frequently (SEC asks for max 10 req/sec)
- Scanner has built-in delays

---

## THE PHILOSOPHY

*"We don't chase. We track. We wait. We strike."*

This scanner catches catalysts WHEN THEY FILE, not when the stock already ran 200%.

SIDU filed the SHIELD contract announcement on Dec 22.  
The stock didn't spike until Dec 26.  
4 DAYS of edge.

That's what we're hunting.

---

**AWOOOO! 🐺**

*No brother falls. The pack hunts together.*

---

## LEGAL

This is a tool for research, not financial advice. Do your own due diligence. Trading involves risk of loss.

Built with love by the Wolf Pack.
