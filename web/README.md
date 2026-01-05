# 🐺 WOLF PACK WEB DASHBOARD
## The Most Badass Trading Dashboard Ever Built

---

## 🎯 WHAT IT IS

A **LIVE, BROWSER-BASED DASHBOARD** that integrates ALL your Wolf Pack scanners into one beautiful interface.

No more running commands. No more terminal outputs. **Just pure visual hunting.**

---

## ⚡ FEATURES

### **1. HIGH CONVICTION SETUPS** 🔥
- Real-time cross-signal validation (70+ scores)
- Shows which signals are active (wounded/insider/8-K/thesis)
- Priority tickers highlighted
- **One glance = Know what to hunt**

### **2. AI FUEL CHAIN HEATMAP** 🌡️
- All 56 tickers across 12 sectors
- Live price updates
- 1-day and 5-day % changes
- Color-coded (green = up, red = down)
- Click any ticker for details

### **3. WOUNDED PREY TRACKER** 🩸
- Tax loss bounce candidates (Jan 2-10 entry window)
- Bounce scores (100 = highest)
- Recovery metrics (5d/10d changes)
- Exit by Jan 31 reminders

### **4. INSIDER CLUSTERS** 👔
- 3+ insiders buying = 🔥 TIGHT CLUSTER
- C-Suite detection
- Total purchases and dollar values
- Cluster classification (Tier 1/2)

### **5. RECENT 8-K CONTRACTS** 📄
- THE 15-MINUTE EDGE in action
- Last 24 hours of high-value filings
- Score + keywords matched
- Direct links to SEC filings

---

## 🚀 HOW TO LAUNCH

### **Option 1: Quick Launch (Recommended)**
```bash
cd /workspaces/trading-companion-2026
chmod +x launch_dashboard.sh
./launch_dashboard.sh
```

Dashboard opens at: **http://localhost:5000**

### **Option 2: Manual Launch**
```bash
cd /workspaces/trading-companion-2026/web
python3 app.py
```

---

## 🎨 WHAT IT LOOKS LIKE

### **Color Scheme:**
- **Background:** Dark gradient (black → navy blue)
- **Cards:** Elevated with hover effects
- **Positive numbers:** Bright green with glow
- **Negative numbers:** Red
- **HIGH CONVICTION:** Rainbow gradient scoring
- **Live status:** Pulsing green badge

### **Layout:**
- **Top:** Wolf Pack header + LIVE HUNTING status
- **Main grid:** Responsive cards (auto-fits screen size)
- **Full-width cards:** HIGH CONVICTION, Heatmap, Wounded Prey
- **Side cards:** Insider Clusters, 8-K Filings
- **Footer:** Wolf Pack branding

---

## 📊 DATA UPDATES

### **Auto-Refresh:**
- Dashboard reloads data every **5 minutes**
- Each card has manual "Refresh" button
- No need to restart

### **Data Sources:**
- **Heatmap:** yfinance live prices
- **Conviction:** cross_signal_validator.py
- **Wounded Prey:** wounded_prey_scanner.py
- **Clusters:** cluster_buy_scanner.py
- **8-K Filings:** sec_8k_contract_scanner.py

---

## 🔧 CUSTOMIZATION

### **Change Refresh Rate:**
Edit `templates/dashboard.html`:
```javascript
// Line ~420 - Change 300000 (5 min) to your preferred milliseconds
setInterval(() => {
    this.loadAll();
}, 300000);  // 5 minutes
```

### **Adjust Thresholds:**
Edit `app.py`:
```python
# Line ~195 - Change HIGH CONVICTION threshold
high_conviction = [r for r in results if r['total_score'] >= 70]

# Line ~214 - Change wounded prey score filter
self.woundedPrey = data.data.filter(p => p.bounce_score >= 60);
```

### **Add New Cards:**
1. Create API endpoint in `app.py`
2. Add card HTML in `templates/dashboard.html`
3. Add data loading function in JavaScript

---

## 🐺 INTEGRATION WITH SCANNERS

### **All scanners work independently:**
```bash
# Run scanners from terminal
cd /workspaces/trading-companion-2026/tools
python3 sec_8k_contract_scanner.py --continuous   # Background
python3 cross_signal_validator.py                 # On demand
python3 wounded_prey_scanner.py                    # Daily
```

### **Dashboard pulls latest data:**
- Scanners update local cache
- Dashboard reads from cache + yfinance
- No conflicts, works in parallel

---

## 📱 MOBILE RESPONSIVE

Dashboard adapts to screen size:
- **Desktop:** Multi-column grid
- **Tablet:** 2-column layout
- **Mobile:** Single column stack

**Works on phone for quick checks!**

---

## ⚙️ TROUBLESHOOTING

### **Port 5000 already in use?**
```bash
# Find what's using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or change port in app.py:
app.run(host='0.0.0.0', port=5001, debug=True)
```

### **Dashboard shows no data?**
1. Run scanners first to populate data
2. Check console for API errors (F12 in browser)
3. Verify Python packages installed: `pip list | grep flask`

### **Slow loading?**
- yfinance API can be slow for many tickers
- Consider caching results (add Redis)
- Or reduce refresh rate

---

## 🚀 DEPLOYMENT (Future)

### **For remote access:**
1. Deploy to cloud (AWS/GCP/DigitalOcean)
2. Use nginx reverse proxy
3. Add SSL certificate
4. Set up authentication

### **For VPS:**
```bash
# Install on Ubuntu server
git clone https://github.com/alexpayne556-collab/trading-companion-2026
cd trading-companion-2026
pip install -r requirements.txt
./launch_dashboard.sh

# Access from anywhere:
http://YOUR_SERVER_IP:5000
```

---

## 🎯 ROADMAP

### **Planned Features:**
- [ ] Real-time price charts (Chart.js integration)
- [ ] Alert notifications (email/SMS when HIGH CONVICTION fires)
- [ ] Historical pattern overlays
- [ ] Portfolio tracker integration
- [ ] Dark/light theme toggle
- [ ] Custom watchlist builder
- [ ] Export to PDF (daily reports)
- [ ] Discord webhook integration

---

## 📚 TECHNICAL STACK

- **Backend:** Flask 3.0+ (Python web framework)
- **Frontend:** Alpine.js 3.x (reactive data binding)
- **Charts:** Chart.js 4.x (future integration)
- **Styling:** Custom CSS with gradients + animations
- **Data:** yfinance + local scanner modules

**No heavy frameworks. Fast, clean, responsive.**

---

## 🐺 WOLF PACK PHILOSOPHY

This dashboard embodies:
- **Build, don't list:** Working solution, not suggestions
- **Ship fast:** v1 shipped, iterate from there
- **Pain begets pain:** Don't add complexity
- **God forgives. Brothers don't:** Execute or answer to the pack

---

## ⚡ THE EDGE VISUALIZED

**Before:** Run 5 scanners, read terminal output, cross-reference manually  
**After:** Open browser, see everything in one dashboard, click to act

That's not convenience. **That's dominance.**

---

🐺 **AWOOOO! HUNT IN STYLE! LLHR!** 🐺

---

**Built with 🐺 by Brokkr**  
**For the Wolf Pack**  
**God forgives. Brothers don't.**
