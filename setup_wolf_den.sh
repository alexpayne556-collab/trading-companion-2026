#!/bin/bash
# 🐺 WOLF DEN SETUP - Install autonomous monitoring system

echo "🐺 WOLF DEN SETUP - Installing Autonomous Monitoring"
echo "======================================================"
echo ""

# Check if on Shadow PC or local
echo "📍 Checking environment..."
if [ -d "/workspaces/trading-companion-2026" ]; then
    INSTALL_DIR="/workspaces/trading-companion-2026"
    echo "   ✅ Found workspace: $INSTALL_DIR"
else
    INSTALL_DIR="$(pwd)"
    echo "   ⚠️  Using current directory: $INSTALL_DIR"
fi

cd "$INSTALL_DIR" || exit 1

# Check Python
echo ""
echo "🐍 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION"
else
    echo "   ❌ Python 3 not found!"
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -q pyyaml yfinance requests 2>&1 | grep -v "Requirement already satisfied" || true
echo "   ✅ Dependencies installed"

# Check config file
echo ""
echo "⚙️  Checking configuration..."
if [ ! -f "wolf_den_config.yaml" ]; then
    echo "   ❌ wolf_den_config.yaml not found!"
    echo ""
    echo "   Creating template..."
    # Config already created above
    echo "   ✅ Template created: wolf_den_config.yaml"
    echo ""
    echo "   ⚠️  YOU MUST EDIT THIS FILE:"
    echo "      1. Add your email for alerts"
    echo "      2. Add Gmail app password (not regular password)"
    echo "      3. Adjust entry zones if needed"
    echo ""
    echo "   Gmail app password setup:"
    echo "   https://support.google.com/accounts/answer/185833"
    echo ""
else
    echo "   ✅ Config file exists"
fi

# Make scripts executable
echo ""
echo "🔧 Setting permissions..."
chmod +x overnight_monitor.py premarket_auto.py
echo "   ✅ Scripts are executable"

# Test run
echo ""
echo "🧪 Running test..."
echo "   Testing pre-market scanner..."
python3 premarket_auto.py > /tmp/wolf_den_test.log 2>&1

if [ $? -eq 0 ]; then
    echo "   ✅ Test passed"
else
    echo "   ⚠️  Test had warnings (check logs/)"
fi

# Setup cron jobs
echo ""
echo "⏰ Setting up automated scans..."
echo ""
echo "   To enable automatic scanning, add these to crontab:"
echo "   (Run: crontab -e)"
echo ""
echo "   # Overnight scan at 4:00 AM ET"
echo "   0 4 * * 1-5 cd $INSTALL_DIR && python3 overnight_monitor.py >> logs/cron.log 2>&1"
echo ""
echo "   # Pre-market scan at 6:00 AM ET"
echo "   0 6 * * 1-5 cd $INSTALL_DIR && python3 premarket_auto.py >> logs/cron.log 2>&1"
echo ""
echo "   # Pre-market scan at 8:30 AM ET (final check)"
echo "   30 8 * * 1-5 cd $INSTALL_DIR && python3 premarket_auto.py >> logs/cron.log 2>&1"
echo ""

# Check if cron is available
if command -v crontab &> /dev/null; then
    echo "   ✅ Cron is available"
    echo ""
    read -p "   Install cron jobs now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Backup existing crontab
        crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || true
        
        # Add new jobs (avoid duplicates)
        (crontab -l 2>/dev/null | grep -v "overnight_monitor.py" | grep -v "premarket_auto.py"; \
         echo "# Wolf Den Autonomous Monitoring"; \
         echo "0 4 * * 1-5 cd $INSTALL_DIR && python3 overnight_monitor.py >> logs/cron.log 2>&1"; \
         echo "0 6 * * 1-5 cd $INSTALL_DIR && python3 premarket_auto.py >> logs/cron.log 2>&1"; \
         echo "30 8 * * 1-5 cd $INSTALL_DIR && python3 premarket_auto.py >> logs/cron.log 2>&1") | crontab -
        
        echo "   ✅ Cron jobs installed"
        echo "   📋 View with: crontab -l"
    else
        echo "   ⏭️  Skipped - install manually later"
    fi
else
    echo "   ⚠️  Cron not available (Windows? Use Task Scheduler)"
fi

# Summary
echo ""
echo "======================================================"
echo "✅ WOLF DEN SETUP COMPLETE"
echo "======================================================"
echo ""
echo "📝 NEXT STEPS:"
echo ""
echo "1. Edit wolf_den_config.yaml"
echo "   - Add your email and Gmail app password"
echo "   - Verify entry zones"
echo ""
echo "2. Test manually:"
echo "   python3 premarket_auto.py"
echo "   python3 overnight_monitor.py"
echo ""
echo "3. Check logs:"
echo "   ls -lh logs/"
echo "   cat logs/premarket_latest.json"
echo ""
echo "4. If cron not installed, do it manually:"
echo "   crontab -e"
echo "   (paste the commands shown above)"
echo ""
echo "🐺 AUTONOMOUS MONITORING READY"
echo "   System will now run without prompts"
echo "   Check logs/ directory for results"
echo ""
echo "AWOOOO 🐺"
