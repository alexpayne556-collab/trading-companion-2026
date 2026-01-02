# 🐺 STREAMLIT DASHBOARD - Deployment Guide

**Access from ANYWHERE. Phone. Laptop. Cloud.**

---

## OPTION 1: Local (Instant - 1 minute)

### Run locally on Shadow PC:

```bash
cd /workspaces/trading-companion-2026

# Install Streamlit
pip install streamlit

# Run dashboard
streamlit run wolf_den_dashboard.py
```

**Access:** http://localhost:8501

---

## OPTION 2: Streamlit Cloud (FREE - 10 minutes)

**Benefits:**
- ✅ Access from phone/laptop anywhere
- ✅ Always on (no Shadow PC needed)
- ✅ FREE for public repos
- ✅ Auto-updates when you push to GitHub

### Setup Steps:

#### 1. Create Streamlit Account (2 min)

Go to: https://streamlit.io/cloud

Click "Sign up with GitHub"

Authorize Streamlit to access your repos.

#### 2. Deploy App (3 min)

1. Click "New app"
2. Select repository: `alexpayne556-collab/trading-companion-2026`
3. Branch: `main`
4. Main file path: `wolf_den_dashboard.py`
5. Click "Deploy!"

#### 3. Add Dependencies (2 min)

Streamlit needs a `requirements.txt` file.

Already created in repo:
```
streamlit
yfinance
pandas
pyyaml
requests
```

If not, create it:
```bash
echo "streamlit
yfinance
pandas
pyyaml
requests" > requirements.txt

git add requirements.txt
git commit -m "Add Streamlit requirements"
git push
```

#### 4. Access Dashboard (1 min)

Your app will be at:
```
https://[your-app-name].streamlit.app
```

Example:
```
https://wolf-den-trading.streamlit.app
```

Save this URL to phone home screen:
- iPhone: Share → Add to Home Screen
- Android: Menu → Add to Home Screen

#### 5. Share URL (optional)

Send URL to pack members.

Make repo public if you want to share dashboard.

---

## OPTION 3: ngrok Tunnel (For testing - 5 minutes)

**Use case:** Access local dashboard from phone without deploying to cloud.

### Setup:

1. Install ngrok:
```bash
# Download from: https://ngrok.com/download
# Or use snap:
snap install ngrok

# Authenticate (free account)
ngrok authtoken YOUR_TOKEN
```

2. Run dashboard locally:
```bash
streamlit run wolf_den_dashboard.py
```

3. In another terminal, create tunnel:
```bash
ngrok http 8501
```

4. Access from phone:
```
https://[random].ngrok.io
```

**Note:** Free ngrok URLs change each time. Streamlit Cloud is better for persistent access.

---

## USAGE

### Morning Routine (2 minutes):

1. Open dashboard on phone: `https://your-app.streamlit.app`

2. Check PRIMARY TARGET status:
   - Price
   - GO/NO-GO decision
   - Conviction breakdown

3. Review conviction rankings:
   - Top 3 tickers for next hunt
   - Insider signals
   - Institutional backing

4. Check pre-market alerts:
   - Any red flags?
   - Volume spikes?
   - Gap moves?

5. Make decision: GO / NO-GO / WAIT

### During Day:

- Refresh dashboard to see updated prices
- Check conviction rankings for next opportunities
- Review institutional changes

### Before Next Hunt:

- Run conviction scan: Click "Run Conviction Scan" in sidebar
- Run 13F scan: Click "Run 13F Scan" in sidebar
- Review top 5 ranked tickers
- Plan next entry

---

## DASHBOARD FEATURES

### 🎯 PRIMARY TARGET
- Live price and change %
- GO/NO-GO status from pre-market scan
- Conviction breakdown (insider, timing, cash, technical)

### 📈 CONVICTION RANKINGS
- All tickers ranked by conviction score (0-100)
- Top 3 highlighted
- Breakdown by category
- Color-coded (🟢 HIGH, 🟡 MODERATE, 🔴 AVOID)

### 🏦 INSTITUTIONAL HOLDINGS
- Top institutional holders for each ticker
- % of float held
- Concentration analysis
- Smart money flows

### 🌅 PRE-MARKET STATUS
- Current pre-market prices
- Volume analysis
- Gap calculations
- GO/NO-GO decisions with reasons

### 🌙 OVERNIGHT ALERTS
- SEC filings (8-K, Form 4)
- News headlines
- Futures status
- Alert levels (RED/YELLOW/GREEN)

### ⚡ QUICK ACTIONS
- Refresh data
- Run conviction scan
- Run 13F scan
- Run pre-market scan
- Auto-refresh toggle

---

## CUSTOMIZATION

### Add More Tickers:

Edit `wolf_den_config.yaml`:
```yaml
watchlist:
  primary: AISP
  backup: [SOUN, BBAI, SMR, IONQ, PLUG]  # Add more here
  positions: [LUNR]
```

Dashboard will automatically show all watchlist tickers.

### Change Refresh Rate:

In dashboard sidebar, toggle "Auto-refresh" and adjust timing in code:
```python
time.sleep(300)  # 300 seconds = 5 minutes
```

### Add Custom Metrics:

Edit `wolf_den_dashboard.py` and add your own sections:
```python
st.header("📊 Custom Analysis")
# Your code here
```

---

## TROUBLESHOOTING

### "Module not found" error:

```bash
pip install streamlit yfinance pandas pyyaml requests
```

### Dashboard won't load:

Check if scanners have run:
```bash
ls -lh logs/*.json
```

If no files, run:
```bash
python3 conviction_ranker.py
python3 institutional_13f_tracker.py
python3 premarket_auto.py
```

### Streamlit Cloud deploy failed:

Check logs in Streamlit Cloud dashboard.

Common issues:
- Missing requirements.txt
- Wrong file path
- Dependency conflicts

Fix and push to GitHub. Streamlit auto-redeploys.

### Can't access from phone:

- Ensure URL is correct: `https://[app-name].streamlit.app`
- Check if repo is public (needed for free tier)
- Try incognito/private mode (clear cache)

---

## COSTS

**Local:** $0 (runs on Shadow PC)

**Streamlit Cloud:** $0 (free for public repos)
- 1 private app free
- Unlimited public apps

**ngrok:** $0 (free tier includes tunneling)

**Total cost:** $0/month

---

## MOBILE APP (Future)

Streamlit supports mobile:
- Add to home screen
- Full-screen mode
- Touch-optimized

For native app (future):
- React Native wrapper
- iOS/Android distribution
- Push notifications

But web dashboard works perfectly on mobile.

---

## SECURITY

**Public repo = public dashboard.**

Don't display:
- Account numbers
- Real dollar amounts
- Personal info

For private dashboard:
- Make repo private
- Use Streamlit Cloud paid plan ($99/year)
- Or self-host on your server

Current setup is fine for:
- Ticker analysis
- Conviction scores
- Public market data

---

## THE DIFFERENCE

**Before:**
- Prompt Brokkr for every update
- Wait for response
- Manual analysis
- No mobile access

**After:**
- Open dashboard on phone
- See all data instantly
- Updated automatically
- Access from anywhere

**This is the standard.**

---

**AWOOOO** 🐺

*"A dashboard in your pocket. A hunt at your fingertips."*
