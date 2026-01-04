# 🐺 Wolf Pack Automation Setup

## REAL AUTOMATION - Not dashboards, ALERTS

**You don't babysit. The system watches. You only act when alerted.**

---

## GitHub Actions (FREE, runs on schedule)

### 1. Overnight Scanner (4:00 AM EST)
**File**: `.github/workflows/overnight_scanner.yml`

**Checks:**
- SEC 8-K filings (AISP)
- Pre-market gaps (>10% = urgent alert)
- Overnight news

**Alerts:**
- 🚨 URGENT: 8-K filed, >10% gap, major news
- 📊 STANDARD: 5-10% gap, minor news
- ✅ SILENT: No activity (lets you sleep)

**Setup:**
```bash
# Add Discord webhook to repo secrets
gh secret set DISCORD_WEBHOOK --body "your_webhook_url"
```

---

### 2. Pre-Market Alert (6:30 AM EST)
**File**: `.github/workflows/premarket_alert.yml`

**Checks:**
- AISP pre-market price
- Entry zone status ($2.70-2.90)
- Volume analysis

**Alerts:**
- ⏰ WAKE UP: Entry zone active OR abort conditions
- 🟡 READY: Near entry, watch at open
- 📊 WATCH: Outside range, monitor

**This WAKES YOU UP only if action needed.**

---

## Discord Alerts (to your phone)

### Setup Discord Webhook

1. **Create Discord server** (if you don't have one)
2. **Create channel**: `#wolf-pack-alerts`
3. **Webhook setup**:
   - Server Settings → Integrations → Webhooks
   - New Webhook → Name: "Wolf Pack Scanner"
   - Copy webhook URL
4. **Add to GitHub secrets**:
   ```bash
   gh secret set DISCORD_WEBHOOK --body "https://discord.com/api/webhooks/..."
   ```

---

## What You Get

### 4:00 AM (Overnight Scanner)
**IF something important happens:**
```
@everyone 🚨 URGENT ALERT 🚨

🚨 AISP: New 8-K filing detected!
🚨 AISP: +12.5% gap!
```

**IF nothing happens:** You sleep. No alert.

---

### 6:30 AM (Pre-Market Alert)
**Entry zone active:**
```
@everyone ⏰ WAKE UP TYR ⏰

🎯 GO GO GO: AISP at $2.85
**ENTRY ZONE ACTIVE** ($2.70-$2.90)
9:45 AM execution window ready!
```

**Gap up too high:**
```
@everyone ⏰ WAKE UP TYR ⏰

🚨 ABORT: AISP gapped to $3.45 (>$3.15)
**TOO EXPENSIVE - Pivot to SOUN backup**
```

**Normal price:**
```
🐺 Pre-Market Update

🟡 READY: AISP at $2.92
Slightly above entry zone. Watch for dip at open.
```

---

## Local Testing (before GitHub Actions)

### Test overnight scanner:
```bash
python3 src/automation/overnight_scanner.py
```

### Test pre-market alert:
```bash
export DISCORD_WEBHOOK="your_webhook_url"
python3 src/automation/premarket_alert.py
```

---

## The Wolf Pack Way

**BEFORE (What I built):**
- Dashboards you stare at ❌
- Manual checks every hour ❌
- Wake up at 4 AM to scan ❌
- Watch clock for 9:45 AM ❌

**AFTER (What you asked for):**
- Scanners run automatically ✅
- Alerts ONLY when action needed ✅
- Sleep until 6:30 AM (or if urgent) ✅
- Focus on research, not execution ✅

---

## Next: Price Target Alerts

**Coming next:**
- 9:45 AM entry window alert ("GO NOW")
- Auto stop-loss monitor (alert if approaching)
- Target hit alerts ($3.50, $4.50, $7.00)
- "Take profit" recommendations

**This is REAL automation. Not toys.**

---

**AWOOOO** 🐺
