#!/bin/bash
# 🐺 MORNING HUNT - Find NEXT week's plays while everyone chases THIS week

echo "🐺 MORNING HUNT - Finding plays 1-2 days early"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# Change to tools directory
cd "$(dirname "$0")"

echo ""
echo "📊 STEP 1: Run all scanners (find unusual activity)"
echo "---"

# Sector Rotation (which sectors are starting to move?)
echo "Running sector_rotation_detector.py..."
python3 sector_rotation_detector.py

echo ""
echo "📈 STEP 2: Options Flow (smart money positioning)"
echo "---"
python3 options_flow_scanner.py

echo ""
echo "📋 STEP 3: Form 4 Insider Buying (executives positioning)"
echo "---"
python3 form4_conviction_scanner.py

echo ""
echo "📰 STEP 4: 8-K Contract News (after-hours deals)"
echo "---"
python3 sec_8k_scanner_v2.py

echo ""
echo "🌙 STEP 5: After-Hours Movers (overnight action)"
echo "---"
python3 after_hours_scanner.py

echo ""
echo "🔍 STEP 6: Pre-Catalyst Hunter (find EARLY plays)"
echo "---"
python3 pre_catalyst_hunter.py --days 7 --min-score 5

echo ""
echo "=========================================="
echo "🐺 HUNT COMPLETE"
echo ""
echo "NOW:"
echo "1. Look for CONFLUENCE (same ticker in multiple scans)"
echo "2. Give list to Fenrir for deep dive"
echo "3. Find plays 2-5 days BEFORE catalyst"
echo "4. Position early, sell into strength"
echo ""
echo "REMEMBER:"
echo "• Don't chase what already ran 10%+"
echo "• Look for quiet accumulation (2-5% moves)"
echo "• Catalyst should be 2+ days away"
echo "• Let the wave pick YOU up"
echo ""
echo "🐺 AWOOOO!"
