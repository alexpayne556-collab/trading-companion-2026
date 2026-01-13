# 🐺 Trading Companion Web Dashboard

**Professional web interface** - No more CLI toys.

## Features

✅ **Real-time Portfolio Monitoring**
- Live positions from Alpaca
- P&L tracking
- Position breakdown

✅ **Live Sonar Scanner** 
- Continuous movement detection
- Whale/Fish/Bass/Nibble classification
- Real-time alerts via WebSocket

✅ **Movement Database Visualization**
- Today's detections
- Historical patterns
- Statistics dashboard

✅ **Bass Fisher Integration**
- 100% validated strategy
- Pattern detection
- Entry signals

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```

Open browser to: **http://localhost:5000**

## Architecture

```
Flask Backend
├── WebSocket (real-time updates)
├── REST API (portfolio, movements, stats)
├── Background Sonar Thread
└── SQLite Movement Database

Frontend
├── Real-time charts
├── Live movement feed
├── Portfolio dashboard
└── Statistics panel
```

## Usage

1. **Start Dashboard**: `python app.py`
2. **Click "Start Sonar"** - Begin scanning
3. **Click "Refresh Portfolio"** - Update positions
4. **Watch movements** appear in real-time

## Endpoints

- `GET /` - Main dashboard
- `GET /api/portfolio` - Portfolio data
- `POST /api/sonar/start` - Start scanning
- `POST /api/sonar/stop` - Stop scanning
- `GET /api/movements/today` - Today's movements
- `GET /api/movements/stats` - Statistics

## WebSocket Events

- `sonar_update` - New movements detected
- `connect` - Client connected
- `disconnect` - Client disconnected

---

**ONE SERIOUS SYSTEM. NO TOYS.**

🐺 AWOOOO
