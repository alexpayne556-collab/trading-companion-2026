# 🐺 NEWS CATALYST TRACKER — V2 IMPROVEMENTS

## What's New

### Old Version (Basic)
- Simple keyword counts (bullish/bearish/AI)
- No weighted scoring
- No sector aggregation
- No contract detection
- Limited AI infrastructure keywords

### V2 (Enhanced for AI Fuel Chain)
✅ **Tier-based catalyst scoring:**
- Tier 1 (3pts): DOE/DOD/NASA contracts, hyperscaler deals, acquisitions
- Tier 2 (2pts): Partnerships, expansions, upgrades, beat/raise
- Tier 3 (1pt): Standard bullish keywords
- Bearish (-2pts): Downgrades, misses, warnings

✅ **Sector-level news aggregation**
- See which AI Fuel Chain sectors are hot in the news
- Track monster catalysts (5+ score) by sector
- Identify sectors with most coverage

✅ **News momentum tracking**
- Which tickers are getting LOTS of coverage (signal)
- 5+ news items = 🔥🔥
- 3+ items = 🔥

✅ **AI Infrastructure keyword detection**
- Nuclear: uranium, SMR, enrichment, NRC
- Cooling: liquid cooling, thermal management, rack density
- Photonics: silicon photonics, 800G, 1.6T, copper wall
- Storage: HBM, HBM3, HBM4, GPU memory
- Chips: AI accelerator, custom silicon
- Quantum: quantum advantage, error correction

✅ **Contract/Government news isolation**
- Separate section for high-value catalysts
- DOE, DOD, NASA, hyperscaler mentions
- Government contract awards

✅ **Better priority ticker watch**
- Enhanced display for your 10 priority tickers
- Score-based sentiment classification
- Time-sorted recent news

---

## Usage

### Full scan (default 24 hours)
```bash
python tools/news_catalyst_tracker_v2.py
```

### Scan last 48 hours
```bash
python tools/news_catalyst_tracker_v2.py 48
```

### Priority tickers only (48h lookback)
```bash
python tools/news_catalyst_tracker_v2.py priority
```

### Just earnings calendar
```bash
python tools/news_catalyst_tracker_v2.py earnings
```

---

## Output Sections

1. **🔥 TOP CATALYSTS** — Highest scored news (monster = 5+)
2. **💰 CONTRACT NEWS** — Government/hyperscaler deals
3. **📊 SECTOR SUMMARY** — Which sectors are hot in news
4. **📰 NEWS MOMENTUM** — Tickers with most coverage
5. **⭐ PRIORITY WATCH** — Your 10 priority tickers
6. **⚠️ WARNINGS** — Bearish news alerts
7. **📅 EARNINGS CALENDAR** — Upcoming earnings

---

## Catalyst Scoring Examples

| News Headline | Score | Why |
|---------------|-------|-----|
| "UUUU wins DOE uranium contract" | +5 | DOE contract (3) + contract (2) |
| "LITE announces Microsoft deal" | +5 | Microsoft (3) + deal (2) |
| "MU beats earnings, raises guidance" | +4 | Beat (2) + raises (2) |
| "OKLO partnership with AWS" | +5 | Partnership (2) + hyperscaler (3) |
| "AMD downgraded by analyst" | -2 | Downgrade (-2) |

---

## When to Use This

- **Sunday night:** Catch weekend news before Monday open
- **After hours:** See what news dropped while markets closed
- **Before earnings:** Check what catalysts are building
- **Daily:** Track which sectors getting media attention

---

## Wolf's Read

**Information moves before price.**

If a ticker is getting 5+ news items in 24 hours = **something's building**.

If a sector has multiple monster catalysts = **money rotating in**.

If you see DOE/DOD/hyperscaler contracts = **thesis validation**.

The wolf that sees the news first, hunts first. 🐺

---

**Created:** January 5, 2026  
**Commit:** 1615571
