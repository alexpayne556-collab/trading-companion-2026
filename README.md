# Trading Companion 2026

A thesis-driven trading research companion. **NOT autonomous trading** — this is a decision support system that helps you:

- Track positions with thesis alignment
- Monitor risk and concentration
- Stay aware of catalysts and deadlines
- Make faster, better-informed decisions

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repo
git clone <your-repo-url>
cd trading-companion-2026

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your Alpaca keys
# Get keys from: https://app.alpaca.markets/paper/dashboard/overview
```

### 3. Test the Setup

```bash
# Verify imports work
python -c "from src.services import PortfolioService; print('✅ Imports OK')"

# Run tests
pytest tests/ -v
```

### 4. Run the Dashboard

```bash
# Start the CLI dashboard
python -m src.cli.dashboard
```

## Project Structure

```
trading-companion-2026/
├── src/
│   ├── config.py              # Settings & environment
│   ├── portfolio/             # Position & portfolio models
│   ├── thesis/                # Thesis tracking
│   ├── integrations/alpaca/   # Alpaca API client
│   ├── risk/                  # Risk rules engine
│   ├── services/              # High-level APIs
│   └── cli/                   # CLI dashboard
├── tests/                     # Test suite
├── data/theses/               # Your thesis YAML files
└── logs/                      # Application logs
```

## Adding Theses

Create YAML files in `data/theses/`:

```yaml
# data/theses/LUNR.yaml
ticker: LUNR
name: Intuitive Machines
thesis: "Successful lunar lander + Space Force contracts = 10x growth"
conviction: HIGH
confidence_score: 8
target_price: 15.0
timeframe_months: 12

catalysts:
  - event: "Lunar landing Jan 8 2026"
    probability: 0.8
    timeline: "immediate"

invalidation:
  - "Launch failure"
  - "Competitor wins exclusive deal"
```

## Risk Alerts

The system monitors for:

| Alert Type | Trigger | Severity |
|------------|---------|----------|
| Concentration | Position > 20% of portfolio | Warning |
| Overnight Move | Price moved > 5% overnight | Warning/Critical |
| Missing Thesis | Position has no documented thesis | Info |
| Target Exceeded | Price exceeded thesis target | Info |

## Development

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Format code
black src/ tests/
isort src/ tests/
```

## License

Private use only.
