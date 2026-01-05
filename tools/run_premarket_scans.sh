#!/bin/bash
# PRE-MARKET SCAN SUITE - Run all scanners
# Usage: ./run_premarket_scans.sh

echo "🐺 BROKKR PRE-MARKET SCAN SUITE"
echo "================================"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S ET')"
echo ""

cd "$(dirname "$0")"

echo "1️⃣ SCANNING SECTOR ROTATION..."
echo "─────────────────────────────────────"
python3 sector_rotation_detector.py
echo ""

echo "2️⃣ SCANNING PRE-MARKET GAPS (≥5%)..."
echo "─────────────────────────────────────"
python3 premarket_gap_scanner.py
echo ""

echo "3️⃣ SCANNING UNUSUAL OPTIONS FLOW..."
echo "─────────────────────────────────────"
python3 options_flow_scanner.py
echo ""

echo "4️⃣ SCANNING INSIDER CONVICTION BUYS (Code P)..."
echo "─────────────────────────────────────"
python3 form4_conviction_scanner.py
echo ""

echo "5️⃣ SCANNING 8-K CONTRACTS (≥$10M, 12h)..."
echo "─────────────────────────────────────"
python3 sec_8k_scanner_v2.py --hours 12
echo ""

echo "✅ ALL SCANS COMPLETE"
echo "🐺 AWOOOO!"
