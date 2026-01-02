#!/bin/bash
# 🐺 Monday Morning Readiness Check
# Run this script to ensure all weapons are loaded before market open

echo "=================================="
echo "🐺 WOLF PACK MONDAY MORNING CHECK"
echo "=================================="
echo ""

cd /workspaces/trading-companion-2026

# 1. Check dashboard is running
echo "1️⃣  Checking dashboard..."
if pgrep -f "streamlit.*wolf_den_war_room" > /dev/null; then
    echo "   ✅ Dashboard running on http://localhost:8501"
else
    echo "   ❌ Dashboard NOT running"
    echo "   Starting dashboard..."
    streamlit run wolf_den_war_room.py --server.headless true --server.port 8501 > /tmp/streamlit.log 2>&1 &
    sleep 5
    echo "   ✅ Dashboard started"
fi
echo ""

# 2. Check databases exist
echo "2️⃣  Checking databases..."
if [ -f "data/insider_transactions.db" ]; then
    INSIDERS=$(sqlite3 data/insider_transactions.db "SELECT COUNT(*) FROM insider_buys")
    echo "   ✅ Insider DB: $INSIDERS transactions"
else
    echo "   ⚠️  No insider database yet - run Form 4 scan"
fi

if [ -f "data/form4_clusters.db" ]; then
    echo "   ✅ Form 4 cluster DB exists"
else
    echo "   ⚠️  No Form 4 cluster DB - will be created on first scan"
fi
echo ""

# 3. Check watchlist file
echo "3️⃣  Checking watchlist..."
if [ -f "atp_watchlists/ATP_WOLF_PACK_MASTER.csv" ]; then
    TICKERS=$(wc -l < atp_watchlists/ATP_WOLF_PACK_MASTER.csv)
    echo "   ✅ Master watchlist: $((TICKERS - 1)) tickers"
else
    echo "   ❌ Master watchlist missing!"
fi
echo ""

# 4. Check critical catalysts loaded
echo "4️⃣  Checking catalysts..."
if [ -f "logs/catalysts/manual_catalysts.json" ]; then
    CATALYST_COUNT=$(python3 -c "import json; data=json.load(open('logs/catalysts/manual_catalysts.json')); print(sum(len(v) for v in data.values()))")
    echo "   ✅ Catalysts loaded: $CATALYST_COUNT events tracked"
    echo "   📅 LUNR IM-3 Mission: Feb 15, 2026"
else
    echo "   ⚠️  No catalysts file - will auto-create on first run"
fi
echo ""

# 5. Check sector rotation data
echo "5️⃣  Checking sector data..."
LATEST_SECTOR=$(ls -t logs/sectors/sector_rotation_*.csv 2>/dev/null | head -1)
if [ -n "$LATEST_SECTOR" ]; then
    SECTOR_DATE=$(basename "$LATEST_SECTOR" | sed 's/sector_rotation_//' | sed 's/.csv//')
    echo "   ✅ Latest sector scan: $SECTOR_DATE"
    
    # Show hot sectors
    echo "   🔥 Hot sectors:"
    python3 -c "
import pandas as pd
df = pd.read_csv('$LATEST_SECTOR')
hot = df.nlargest(3, '5d_pct')
for _, row in hot.iterrows():
    print(f\"      {row['Sector']}: +{row['5d_pct']:.1f}%\")
" 2>/dev/null || echo "      (Run sector scan for latest)"
else
    echo "   ⚠️  No sector data - run sector scan"
fi
echo ""

# 6. Test Wolf Intelligence
echo "6️⃣  Testing Wolf Intelligence..."
WOLF_TEST=$(python3 src/research/wolf_intelligence.py LUNR 2>&1 | head -5 | tail -1)
if [[ $WOLF_TEST == *"LUNR"* ]]; then
    echo "   ✅ Wolf Intelligence operational"
else
    echo "   ❌ Wolf Intelligence error"
fi
echo ""

# 7. Quick conviction test
echo "7️⃣  Quick conviction test on top targets..."
echo "   Testing: GOGO, LUNR, SMR"
for TICKER in GOGO LUNR SMR; do
    SCORE=$(python3 src/research/wolf_intelligence.py $TICKER 2>&1 | grep "^$TICKER:" | awk '{print $2}')
    if [ -n "$SCORE" ]; then
        echo "      $TICKER: $SCORE"
    else
        echo "      $TICKER: ⚠️  Error"
    fi
done
echo ""

# 8. Monday morning action items
echo "=================================="
echo "📋 MONDAY MORNING ACTION ITEMS"
echo "=================================="
echo ""
echo "1. Open dashboard: http://localhost:8501"
echo "2. Check 'Sectors' tab - which sectors are hot?"
echo "3. Run Form 4 scan:"
echo "   python src/research/form4_realtime_scanner.py --scan --detect"
echo ""
echo "4. Check Monitor tab for overnight moves"
echo "5. Run unified intelligence on watchlist:"
echo "   python src/research/wolf_intelligence.py TICKER"
echo ""
echo "6. Review top 5 conviction targets in dashboard"
echo "7. Check catalyst calendar for this week"
echo ""
echo "=================================="
echo "🎯 PRIMARY TARGETS FOR JAN 3, 2026"
echo "=================================="
echo ""
echo "1. GOGO - Executive Chair buying, wounded prey"
echo "   • Earnings: Feb 12"
echo "   • Setup: Insider conviction + low price"
echo ""
echo "2. LUNR - IM-3 Moon Mission Feb 15"
echo "   • Position: Already holding 10 shares"
echo "   • Catalyst: 44 days out"
echo ""
echo "3. AISP - Already ran from \$2.70 to \$3.14"
echo "   • Status: MISSED (ran Wednesday)"
echo "   • Lesson: Need faster alerts"
echo ""
echo "=================================="
echo "LLHR 🐺"
echo "=================================="
