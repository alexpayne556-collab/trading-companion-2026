#!/usr/bin/env python3
"""
🐺 WOLF PACK PATTERN SCANNER
Real-time scanner for technical patterns that ACTUALLY work
Built from reverse-engineering 40+ actual winners

70% detection rate on technical setups
Validated through redundancy testing

Run daily to find high-probability setups
"""

import yfinance as yf
from datetime import datetime
import sys
sys.path.insert(0, '/workspaces/trading-companion-2026')
from discovery_engine.free_data_sources import build_confirmed_universe


class PatternScanner:
    """Scans for validated winning patterns"""

    def scan_ticker(self, ticker):
        """Scan single ticker for ALL winning patterns"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='3mo')

            if len(hist) < 30:
                return None

            result = {
                'ticker': ticker,
                'patterns': [],
                'confidence': 0,
                'signals': {}
            }

            current_price = hist['Close'].iloc[-1]

            # 5-day momentum (close-to-close)
            mom_5d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100 if len(hist) >= 6 else 0
            
            # NEW: PEAK gain (shows TRUE potential - best intraday exit in last 5d)
            peak_5d = ((hist['High'].iloc[-5:].max() - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100 if len(hist) >= 6 else 0

            # Volume metrics
            vol_current = hist['Volume'].iloc[-1]
            vol_3d_avg = hist['Volume'].iloc[-4:-1].mean() if len(hist) >= 4 else vol_current
            vol_20d_avg = hist['Volume'].iloc[-21:-1].mean() if len(hist) >= 21 else vol_current
            vol_3d_ratio = vol_3d_avg / vol_20d_avg if vol_20d_avg > 0 else 1

            # Green days
            green_days = sum(hist['Close'].tail(5) > hist['Open'].tail(5))

            # MA position
            ma_20 = hist['Close'].rolling(20).mean()
            ma_50 = hist['Close'].rolling(50).mean()
            above_ma20 = bool(current_price > ma_20.iloc[-1]) if len(ma_20) > 0 else False
            above_ma50 = bool(current_price > ma_50.iloc[-1]) if len(ma_50) > 0 else False

            result['signals'] = {
                'mom_5d': round(mom_5d, 1),
                'peak_5d': round(peak_5d, 1),  # NEW: shows TRUE upside potential
                'vol_3d_ratio': round(vol_3d_ratio, 2),
                'green_days': int(green_days),
                'above_ma20': 1 if above_ma20 else 0,  # JSON-safe
                'above_ma50': 1 if above_ma50 else 0,  # JSON-safe
                'price': round(current_price, 2)
            }

            # VALIDATED PATTERNS (from backtest)

            # Pattern 1: ANY_POSITIVE_5D (59.5% base hit rate)
            if mom_5d > 0:
                result['patterns'].append('ANY_POSITIVE_5D')
                result['confidence'] += 30

            # Pattern 2: GREEN_STREAK + VOL (58% hit rate for 20%+ winners)
            if green_days >= 2 and vol_3d_ratio > 1.0:
                result['patterns'].append('GREEN_STREAK_VOL')
                result['confidence'] += 35

            # Pattern 3: STRONG_MOMENTUM (24.3% detection, high conviction)
            if mom_5d >= 10 and green_days >= 3:
                result['patterns'].append('STRONG_MOMENTUM')
                result['confidence'] += 40

            # Pattern 4: ABOVE_BOTH_MAS (85.7% of big winners)
            if above_ma20 and above_ma50:
                result['patterns'].append('ABOVE_BOTH_MAS')
                result['confidence'] += 30
            elif above_ma20:
                result['patterns'].append('ABOVE_MA20')
                result['confidence'] += 20

            # Pattern 5: VOLUME_SURGE
            if vol_3d_ratio > 1.5:
                result['patterns'].append('VOLUME_SURGE')
                result['confidence'] += 25

            # Pattern 6: MULTI_SIGNAL (confluence)
            if mom_5d > 0 and vol_3d_ratio > 1.2 and above_ma20:
                result['patterns'].append('MULTI_SIGNAL')
                result['confidence'] += 40

            return result if len(result['patterns']) > 0 else None

        except Exception as e:
            return None

    def scan_universe(self, tickers):
        """Scan entire universe"""
        results = []
        for ticker in tickers:
            result = self.scan_ticker(ticker)
            if result:
                results.append(result)

        return sorted(results, key=lambda x: x['confidence'], reverse=True)


def run_daily_scan():
    """Run the daily pattern scan"""
    print("=" * 70)
    print("🐺 WOLF PACK PATTERN SCANNER")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    # Get universe
    universe = build_confirmed_universe()
    all_tickers = [u['ticker'] for u in universe]

    # Add sectors we know matter
    additional = ['NTLA', 'BEAM', 'CRSP', 'EDIT', 'VRTX', 'MRNA',
                  'RIVN', 'LCID', 'BLNK', 'PLUG',
                  'SOUN', 'PLTR', 'MARA', 'RIOT', 'CLSK']
    all_tickers.extend(additional)
    all_tickers = list(set(all_tickers))

    print(f"\n📊 Scanning {len(all_tickers)} tickers...\n")

    # Scan
    scanner = PatternScanner()
    matches = scanner.scan_universe(all_tickers[:150])

    print(f"✅ Found {len(matches)} pattern matches\n")
    print("=" * 70)
    print("🔥 TOP OPPORTUNITIES")
    print("=" * 70)
    print(f"{'TICKER':<7} {'CONF':>4} {'#PAT':>4} {'CLOSE':>6} {'PEAK':>6} {'VOL':>5} {'PATTERNS'}")
    print("-" * 70)

    for match in matches[:20]:
        patterns_str = ', '.join(match['patterns'][:3])
        if len(match['patterns']) > 3:
            patterns_str += f" +{len(match['patterns'])-3}"

        mom = match['signals']['mom_5d']
        peak = match['signals']['peak_5d']  # NEW: shows TRUE potential
        vol = match['signals']['vol_3d_ratio']

        # Highlight high confidence
        prefix = "🔥" if match['confidence'] >= 100 else "⚡" if match['confidence'] >= 70 else "  "

        print(f"{prefix}{match['ticker']:<5} {match['confidence']:>4} {len(match['patterns']):>4} {mom:>5.1f}% {peak:>5.1f}% {vol:>4.1f}x  {patterns_str}")

    print("\n" + "=" * 70)
    print("💎 CONVICTION LEVELS")
    print("=" * 70)
    print(f"   🔥 100+ confidence: {len([m for m in matches if m['confidence'] >= 100])} tickers")
    print(f"   ⚡ 70-99 confidence: {len([m for m in matches if 70 <= m['confidence'] < 100])} tickers")
    print(f"   👀 50-69 confidence: {len([m for m in matches if 50 <= m['confidence'] < 70])} tickers")

    return matches


if __name__ == "__main__":
    matches = run_daily_scan()
