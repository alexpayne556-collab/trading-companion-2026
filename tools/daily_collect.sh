#!/bin/bash
# 🐺 Daily collection cron job
# Add this to your crontab to run every day at market close

# Run at 4:30 PM EST (after market close)
# 30 16 * * 1-5 /workspaces/trading-companion-2026/tools/daily_collect.sh

cd /workspaces/trading-companion-2026

# Collect data
python tools/data_collector.py collect >> logs/collector.log 2>&1

# Optional: Run analysis if it's Friday
if [ "$(date +%u)" -eq 5 ]; then
    python tools/data_collector.py index >> logs/collector.log 2>&1
fi

echo "Collection complete: $(date)" >> logs/collector.log
