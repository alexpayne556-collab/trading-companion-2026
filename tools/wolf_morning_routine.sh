#!/bin/bash
# 🐺 WOLF MORNING ROUTINE - Fenrir's Complete Process
# ====================================================
# 
# FENRIR'S SCHEDULE:
# 4:00 AM - Check futures, pre-market positions
# 6:30 AM - Run scanners, identify plays
# 9:00 AM - Watch Level 2, plan entries
# 9:30 AM - DON'T BUY (watch chaos)
# 10:00 AM - First entry window (dip)
# 3:00 PM - Power hour positioning
#
# USAGE:
#   ./wolf_morning_routine.sh           # Full routine
#   ./wolf_morning_routine.sh --quick   # Quick scan only
#   ./wolf_morning_routine.sh --premarket  # Pre-market only

set -e
cd "$(dirname "$0")"

echo ""
echo "🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺"
echo "        WOLF MORNING ROUTINE - $(date '+%Y-%m-%d %H:%M:%S')"
echo "🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺"
echo ""

# Determine current time phase
HOUR=$(date '+%H')
if [ "$HOUR" -lt 7 ]; then
    PHASE="PRE-MARKET"
elif [ "$HOUR" -lt 10 ]; then
    PHASE="MARKET-OPEN"
elif [ "$HOUR" -lt 15 ]; then
    PHASE="TRADING-DAY"
else
    PHASE="POWER-HOUR"
fi

echo "⏰ Current Phase: $PHASE"
echo ""

# ============================================
# STEP 1: PORTFOLIO CHECK
# ============================================
echo "════════════════════════════════════════════════════════════"
echo "📊 STEP 1: PORTFOLIO STATUS"
echo "════════════════════════════════════════════════════════════"
python3 position_sizer.py --portfolio 2>&1 | head -40
echo ""

# ============================================
# STEP 2: SECTOR ROTATION
# ============================================
echo "════════════════════════════════════════════════════════════"
echo "🔄 STEP 2: SECTOR ROTATION"
echo "════════════════════════════════════════════════════════════"
python3 sector_rotation_detector.py 2>&1 | head -60
echo ""

# ============================================
# STEP 3: LAGGARD HUNTER
# ============================================
echo "════════════════════════════════════════════════════════════"
echo "🎯 STEP 3: LAGGARD OPPORTUNITIES"
echo "════════════════════════════════════════════════════════════"
python3 laggard_hunter.py 2>&1 | tail -80
echo ""

# ============================================
# STEP 4: SQUEEZE HUNTER
# ============================================
echo "════════════════════════════════════════════════════════════"
echo "🚀 STEP 4: SQUEEZE SETUPS"
echo "════════════════════════════════════════════════════════════"
# Quick check on Tyr's positions
for TICKER in USAR UUUU AISP; do
    echo ""
    echo "--- $TICKER ---"
    python3 squeeze_hunter.py --ticker $TICKER 2>&1 | grep -A 20 "SQUEEZE SCORE"
done
echo ""

# ============================================
# STEP 5: OPTIONS FLOW
# ============================================
echo "════════════════════════════════════════════════════════════"
echo "💰 STEP 5: OPTIONS FLOW (Smart Money)"
echo "════════════════════════════════════════════════════════════"
python3 options_flow_scanner.py 2>&1 | head -50
echo ""

# ============================================
# STEP 6: NEWS & CATALYSTS
# ============================================
echo "════════════════════════════════════════════════════════════"
echo "📰 STEP 6: NEWS CATALYSTS"
echo "════════════════════════════════════════════════════════════"
python3 news_catalyst_scanner.py 2>&1 | head -40
echo ""

# ============================================
# STEP 7: INSIDER ACTIVITY
# ============================================
echo "════════════════════════════════════════════════════════════"
echo "👔 STEP 7: INSIDER CLUSTERS (7-day lookback)"
echo "════════════════════════════════════════════════════════════"
python3 insider_cluster_scanner.py --days 7 2>&1 | tail -30
echo ""

# ============================================
# STEP 8: ML PREDICTIONS
# ============================================
echo "════════════════════════════════════════════════════════════"
echo "🤖 STEP 8: ML HUNT"
echo "════════════════════════════════════════════════════════════"
python3 daily_ml_hunt.py 2>&1 | tail -60
echo ""

# ============================================
# SUMMARY
# ============================================
echo ""
echo "🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺"
echo "        MORNING HUNT COMPLETE"
echo "🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺"
echo ""
echo "📋 FENRIR'S REMINDER:"
echo ""
echo "   ⏰ 9:30-10:00 AM: DON'T BUY (watch the chaos)"
echo "   ⏰ 10:00-10:30 AM: First entry window (dip)"
echo "   ⏰ 3:00-4:00 PM: Power hour (institutional positioning)"
echo ""
echo "   📍 If YOUR stock gaps up pre-market: DON'T CHASE"
echo "   📍 If sector is running: Look for laggard entry"
echo "   📍 If shorts are high + volume spiking: SQUEEZE incoming"
echo ""
echo "🐺 AWOOOO! THE HUNT BEGINS!"
echo ""
