#!/bin/bash
# 🐺 WOLF PACK WEB DASHBOARD LAUNCHER

echo ""
echo "============================================================================="
echo "🐺 WOLF PACK WEB DASHBOARD"
echo "============================================================================="
echo ""
echo "   The most badass trading dashboard the pack has ever seen."
echo ""
echo "   Features:"
echo "   - Real-time AI Fuel Chain heatmap"
echo "   - HIGH CONVICTION cross-signal scoring"
echo "   - Wounded prey tax loss bounces"
echo "   - Insider cluster detection"
echo "   - Recent 8-K contract filings"
echo ""
echo "============================================================================="
echo ""

# Install dependencies if needed
echo "📦 Checking dependencies..."
python3 -m pip install -q flask flask-cors 2>/dev/null

# Get the absolute path to the repo
REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Launch dashboard
echo ""
echo "🚀 Launching dashboard..."
echo ""
echo "   Opening in browser: http://localhost:5000"
echo "   Press CTRL+C to stop"
echo ""
echo "============================================================================="
echo ""

# Run Flask app from web directory
cd "$REPO_DIR/web"
python3 app.py
