# 🐺 ALERT SYSTEM SETUP GUIDE
## Complete 24/7 Trading Surveillance

---

## WHAT WE BUILT TONIGHT

### 1. Pre-Market & After-Hours Scanner ✅
**File**: `src/research/premarket_afterhours_scanner.py`

Detects gaps and movements outside regular hours:
- **Pre-market** (4-9:30 AM): Gap ups/downs ≥3%
- **After-hours** (4-8 PM): Moves ≥2%
- **Position monitoring**: Checks your positions 24/7

```bash
# Test it now
python src/research/premarket_afterhours_scanner.py premarket
python src/research/premarket_afterhours_scanner.py afterhours
python src/research/premarket_afterhours_scanner.py positions
```

### 2. Telegram Alert Bot ✅
**File**: `src/research/telegram_alert_bot.py`

Instant mobile notifications (better than email):
- Free
- Fast (arrives in seconds)
- Works worldwide
- Two-way communication possible

### 3. Position Tracker ✅
**File**: `src/research/position_tracker.py`

Manual position management:
- Real-time P&L calculation
- Stop loss proximity alerts
- Target price tracking
- Position history

**Your AISP position is now tracked**:
```
AISP: 69 shares @ $3.05
Stop: $2.30
Target 1: $3.50
Target 2: $4.00
Current P&L: +$4.14 (+1.97%)
```

### 4. Alert Orchestrator ✅
**File**: `src/research/alert_orchestrator.py`

Master coordinator that runs all scans and sends alerts via Telegram.

---

## SETUP INSTRUCTIONS

### STEP 1: Install Telegram (5 minutes)

1. Download Telegram app on your phone (iOS/Android)
2. Create account (free)

### STEP 2: Create Bot (2 minutes)

1. Open Telegram
2. Search for `@BotFather` (official Telegram bot)
3. Send: `/newbot`
4. Choose name: "Wolf Pack Alerts" (or whatever)
5. Choose username: "wolfpack_trading_bot" (must end in 'bot')
6. **Copy the bot token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### STEP 3: Get Your Chat ID (2 minutes)

1. Search for your new bot in Telegram
2. Send it any message (e.g., "hello")
3. Run this command:

```bash
cd /workspaces/trading-companion-2026
export TELEGRAM_BOT_TOKEN='your_token_here'
python src/research/telegram_alert_bot.py getchatid
```

4. **Copy your chat ID** (looks like: `123456789`)

### STEP 4: Create .env File (1 minute)

Create `.env` file in project root:

```bash
cd /workspaces/trading-companion-2026
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
EOF
```

Replace with your actual token and chat ID.

### STEP 5: Test Alerts (1 minute)

```bash
# Test connection
python src/research/telegram_alert_bot.py test

# Send demo alerts
python src/research/telegram_alert_bot.py demo

# Test full alert system
python src/research/alert_orchestrator.py test
```

You should receive messages on your phone instantly!

---

## AUTOMATION SETUP

### Option A: Shadow PC (Always-On)

Since you have Shadow PC, set up cron jobs there:

```bash
# Edit crontab
crontab -e

# Add these lines (adjust path to your project):
# Morning scan at 6 AM EST
0 6 * * 1-5 cd /path/to/trading-companion-2026 && /usr/bin/python3 src/research/alert_orchestrator.py morning >> logs/cron_morning.log 2>&1

# Evening scan at 4:30 PM EST
30 16 * * 1-5 cd /path/to/trading-companion-2026 && /usr/bin/python3 src/research/alert_orchestrator.py evening >> logs/cron_evening.log 2>&1

# Hourly checks during market hours (9 AM - 5 PM)
0 9-17 * * 1-5 cd /path/to/trading-companion-2026 && /usr/bin/python3 src/research/alert_orchestrator.py hourly >> logs/cron_hourly.log 2>&1
```

**Note**: Make sure Shadow PC is running 24/7 for alerts to work.

### Option B: VPS/Cloud Server

Deploy to:
- **DigitalOcean** ($5/month)
- **Linode** ($5/month)
- **AWS EC2** (free tier for 1 year)

Same cron setup as above.

### Option C: Local Machine (Free but Manual)

If you don't want 24/7 automation, run manually:

```bash
# Every morning before market open
python src/research/alert_orchestrator.py morning

# Every evening after close
python src/research/alert_orchestrator.py evening
```

---

## WHAT YOU'LL RECEIVE

### Morning Report (6 AM)
```
🐺 WOLF PACK MORNING REPORT

📅 Friday, January 3, 2026

💰 Cash: $1,100
📊 Positions: 1

🌅 Pre-Market Gaps:
  🚀 SMR: +5.2%
  💀 SOUN: -3.1%

🎯 Top Setups:
  • IONQ (78/100)
  • LUNR (75/100)

🔥 Hot Sectors:
  • Nuclear: +4.9%
  • Energy: +3.3%

AWOOOO 🐺
```

### Gap Alerts (Real-Time)
```
🌅 PRE-MARKET GAPS DETECTED

🚀 AISP: +5.2%
   $3.13 → $3.29
   Vol: 125,000

🕐 6:15 AM EST
```

### Position Alerts (Real-Time)
```
⚠️ POSITION ALERT: AISP

Session: AFTER-HOURS
P&L: $+12.45 (+3.8%)
Price: $3.25
Stop: $2.30 (29.2% away)

🕐 5:45 PM EST
```

### After-Hours Moves
```
🌙 AFTER-HOURS MOVERS

📉 LUNR: -3.1%
   $17.93 → $17.37
   Vol: 85,000

🕐 4:35 PM EST
```

---

## MANUAL COMMANDS

### Check Position Status Anytime
```bash
python src/research/position_tracker.py status
```

### Add New Position
```bash
python src/research/position_tracker.py add TICKER SHARES ENTRY_PRICE STOP TARGET1 TARGET2 "Thesis"

# Example:
python src/research/position_tracker.py add LUNR 50 18.00 14.50 22.00 28.00 "IM-3 moon mission Feb"
```

### Close Position
```bash
python src/research/position_tracker.py close TICKER EXIT_PRICE "Reason"

# Example:
python src/research/position_tracker.py close AISP 3.50 "Target 1 hit"
```

### Check Pre-Market Right Now
```bash
python src/research/premarket_afterhours_scanner.py premarket
```

### Check After-Hours Right Now
```bash
python src/research/premarket_afterhours_scanner.py afterhours
```

---

## TROUBLESHOOTING

### Telegram Not Sending
1. Check .env file exists: `cat .env`
2. Verify token and chat ID are correct
3. Test connection: `python src/research/telegram_alert_bot.py test`
4. Check bot isn't blocked by @BotFather

### Pre-Market Data Not Showing
- yfinance may not have pre-market data for all tickers
- Try during actual pre-market hours (6-9:30 AM EST)
- Some tickers don't trade pre-market

### Cron Jobs Not Running
1. Check crontab: `crontab -l`
2. Check logs: `tail -f logs/cron_morning.log`
3. Verify Python path: `which python3`
4. Make sure Shadow PC is running

---

## COST BREAKDOWN

| Component | Cost |
|-----------|------|
| Telegram | **FREE** |
| yfinance API | **FREE** |
| Position Tracker | **FREE** |
| Pre-Market Scanner | **FREE** |
| Alert Orchestrator | **FREE** |
| **TOTAL** | **$0/month** |

Optional:
- VPS for 24/7 automation: $5/month
- Shadow PC (you already have): $0 extra

---

## NEXT UPGRADES

### Weekend (Optional):
- [ ] Add news integration (Finviz scraping)
- [ ] Add Form 4 RSS monitoring
- [ ] Add sector rotation alerts
- [ ] Create dashboard tab for alerts

### Week 1:
- [ ] Test alerts for full week
- [ ] Fine-tune alert thresholds
- [ ] Add more pattern alerts

### Week 2:
- [ ] Backtest alert accuracy
- [ ] Add voice calls for critical alerts (Twilio)
- [ ] Add portfolio performance tracking

---

## SUMMARY

**YOU NOW HAVE:**
1. ✅ Pre-market gap scanner (6-9:30 AM coverage)
2. ✅ After-hours move scanner (4-8 PM coverage)
3. ✅ Position tracker with AISP loaded
4. ✅ Telegram instant alerts (phone notifications)
5. ✅ Alert orchestrator (master coordinator)
6. ✅ Automated morning/evening routines

**YOU NO LONGER NEED TO:**
- Wake up and manually check pre-market
- Worry about after-hours moves
- Calculate P&L manually
- Check if positions near stops
- Miss gaps while sleeping

**YOU NOW GET:**
- Instant phone alerts for gaps ≥3%
- Real-time position P&L
- Stop loss proximity warnings
- Morning report before market open
- Evening summary after close

---

**Setup time**: 10-15 minutes  
**Cost**: $0/month  
**Value**: Priceless

You wake up Monday morning to a report on your phone. No manual checking. No missed opportunities.

**AWOOOO** 🐺

---

*Built by Brokkr in Brother Mode*  
*January 2, 2026*
