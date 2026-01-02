#!/usr/bin/env python3
"""
🐺 WOLF INTELLIGENCE - Cross-System Conviction Layer
Combines insider + sector + catalyst + technical for unified scoring

This is the brain that makes all weapons work together
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

class WolfIntelligence:
    """
    Unified intelligence layer
    Answers: Should I hunt this prey NOW or wait?
    """
    
    def __init__(self):
        self.data_dir = Path('data')
        self.logs_dir = Path('logs')
        
    def calculate_unified_conviction(self, ticker: str) -> Dict:
        """
        Master conviction calculator
        Combines all systems for one authoritative score
        
        Returns dict with score breakdown and actionable verdict
        """
        conviction = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'total_score': 0,
            'verdict': '',
            'timeframe': '',
            'risks': []
        }
        
        # Component 1: Insider Buying Score (0-40 points)
        insider_score = self._score_insider_activity(ticker)
        conviction['components']['insider'] = insider_score
        
        # Component 2: Sector Momentum (0-15 points)
        sector_score = self._score_sector_momentum(ticker)
        conviction['components']['sector'] = sector_score
        
        # Component 3: Catalyst Proximity (0-15 points)
        catalyst_score = self._score_catalyst_timing(ticker)
        conviction['components']['catalyst'] = catalyst_score
        
        # Component 4: Technical Setup (0-20 points)
        technical_score = self._score_technical_setup(ticker)
        conviction['components']['technical'] = technical_score
        
        # Component 5: Failed Breakout Bonus (0-10 points)
        breakout_score = self._score_failed_breakout(ticker)
        conviction['components']['breakout'] = breakout_score
        
        # Total
        conviction['total_score'] = sum([
            insider_score.get('score', 0),
            sector_score.get('score', 0),
            catalyst_score.get('score', 0),
            technical_score.get('score', 0),
            breakout_score.get('score', 0)
        ])
        
        # Generate verdict
        conviction['verdict'] = self._generate_verdict(conviction['total_score'])
        conviction['timeframe'] = self._suggest_timeframe(conviction['components'])
        conviction['risks'] = self._identify_risks(conviction['components'])
        
        return conviction
    
    def _score_insider_activity(self, ticker: str) -> Dict:
        """Score insider buying patterns"""
        score_data = {'score': 0, 'details': []}
        
        try:
            db_path = self.data_dir / 'insider_transactions.db'
            if not db_path.exists():
                return score_data
            
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            # Get last 14 days of buys
            cutoff = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
            c.execute('''
                SELECT insider_name, insider_title, SUM(value) as total_value,
                       COUNT(*) as num_buys, MAX(transaction_date) as latest
                FROM insider_buys
                WHERE ticker = ? AND transaction_date >= ?
                GROUP BY insider_name
                ORDER BY total_value DESC
            ''', (ticker, cutoff))
            
            insiders = c.fetchall()
            conn.close()
            
            if not insiders:
                return score_data
            
            # Scoring logic
            base_score = 0
            
            # Multiple insiders = strong signal
            num_insiders = len(insiders)
            if num_insiders >= 3:
                base_score += 25  # AISP-level setup
                score_data['details'].append(f"🔥 CLUSTER: {num_insiders} insiders")
            elif num_insiders == 2:
                base_score += 15
                score_data['details'].append(f"✅ {num_insiders} insiders")
            else:
                base_score += 10
            
            # Total dollar amount
            total_value = sum(i[2] for i in insiders)
            if total_value > 1000000:
                base_score += 10
                score_data['details'].append(f"💰 ${total_value/1e6:.1f}M invested")
            elif total_value > 500000:
                base_score += 5
            
            # CEO/Founder buys worth more than CFO
            for insider in insiders:
                title = insider[1].upper()
                if any(role in title for role in ['CEO', 'FOUNDER', 'PRESIDENT', 'CHAIR']):
                    base_score += 5
                    score_data['details'].append(f"👔 {insider[1]}: ${insider[2]/1000:.0f}k")
                    break
            
            # Recency bonus
            latest_buy = insiders[0][4]
            days_ago = (datetime.now() - datetime.strptime(latest_buy, '%Y-%m-%d')).days
            if days_ago <= 3:
                base_score += 5
                score_data['details'].append(f"⚡ Recent: {days_ago}d ago")
            
            score_data['score'] = min(base_score, 40)  # Cap at 40
            
        except Exception as e:
            score_data['details'].append(f"⚠️ Error: {e}")
        
        return score_data
    
    def _score_sector_momentum(self, ticker: str) -> Dict:
        """Score sector momentum"""
        score_data = {'score': 0, 'details': []}
        
        try:
            # Read latest sector rotation
            sector_files = sorted((self.logs_dir / 'sectors').glob('sector_rotation_*.csv'))
            if not sector_files:
                return score_data
            
            latest = pd.read_csv(sector_files[-1])
            
            # Map ticker to sector (simplified - enhance later)
            sector_map = {
                'SMR': 'Nuclear', 'OKLO': 'Nuclear', 'CCJ': 'Nuclear',
                'LUNR': 'Space', 'RKLB': 'Space', 'ASTS': 'Space',
                'IONQ': 'Quantum', 'QBTS': 'Quantum', 'RGTI': 'Quantum',
                'KTOS': 'Defense', 'AVAV': 'Defense', 'LMT': 'Defense'
            }
            
            sector = sector_map.get(ticker)
            if not sector:
                return score_data
            
            # Find sector performance
            sector_row = latest[latest['Sector'].str.contains(sector, case=False, na=False)]
            if sector_row.empty:
                return score_data
            
            perf_5d = sector_row.iloc[0].get('5d_pct', 0)
            
            if perf_5d > 5:
                score_data['score'] = 15
                score_data['details'].append(f"🔥 {sector} +{perf_5d:.1f}% (HOT)")
            elif perf_5d > 3:
                score_data['score'] = 10
                score_data['details'].append(f"✅ {sector} +{perf_5d:.1f}%")
            elif perf_5d > 0:
                score_data['score'] = 5
                score_data['details'].append(f"➡️ {sector} +{perf_5d:.1f}%")
            else:
                score_data['details'].append(f"❄️ {sector} {perf_5d:.1f}%")
            
        except Exception as e:
            score_data['details'].append(f"⚠️ Error: {e}")
        
        return score_data
    
    def _score_catalyst_timing(self, ticker: str) -> Dict:
        """Score upcoming catalysts"""
        score_data = {'score': 0, 'details': []}
        
        try:
            catalyst_file = self.logs_dir / 'catalysts' / 'manual_catalysts.json'
            if not catalyst_file.exists():
                return score_data
            
            with open(catalyst_file) as f:
                catalysts = json.load(f)
            
            if ticker not in catalysts:
                return score_data
            
            today = datetime.now().date()
            
            for event in catalysts[ticker]:
                date_str = event['date']
                
                try:
                    if 'Q' in date_str:
                        # Quarter - give medium score
                        score_data['score'] += 5
                        score_data['details'].append(f"📅 {event['event']} ({date_str})")
                    else:
                        event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        days_until = (event_date - today).days
                        
                        if 1 <= days_until <= 7:
                            score_data['score'] += 15
                            score_data['details'].append(f"🚀 {event['event']} in {days_until}d!")
                        elif 8 <= days_until <= 14:
                            score_data['score'] += 10
                            score_data['details'].append(f"📍 {event['event']} in {days_until}d")
                        elif 15 <= days_until <= 30:
                            score_data['score'] += 5
                            score_data['details'].append(f"📌 {event['event']} in {days_until}d")
                        elif 31 <= days_until <= 60:
                            score_data['score'] += 3
                            score_data['details'].append(f"📅 {event['event']} in {days_until}d")
                except:
                    pass
            
            score_data['score'] = min(score_data['score'], 15)  # Cap at 15
            
        except Exception as e:
            score_data['details'].append(f"⚠️ Error: {e}")
        
        return score_data
    
    def _score_technical_setup(self, ticker: str) -> Dict:
        """Score technical setup - placeholder for now"""
        score_data = {'score': 0, 'details': []}
        
        try:
            import yfinance as yf
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period='3mo')
            
            if len(hist) < 20:
                return score_data
            
            current = hist['Close'].iloc[-1]
            high_52w = hist['High'].max()
            low_52w = hist['Low'].min()
            
            # Distance from 52w low (wounded prey)
            distance_from_low = ((current - low_52w) / low_52w) * 100
            
            if distance_from_low < 15:
                score_data['score'] += 15
                score_data['details'].append(f"🩸 {distance_from_low:.1f}% from 52w low (wounded)")
            elif distance_from_low < 25:
                score_data['score'] += 10
                score_data['details'].append(f"📉 {distance_from_low:.1f}% from low")
            elif distance_from_low < 40:
                score_data['score'] += 5
            
            # Volume surge
            recent_vol = hist['Volume'].tail(5).mean()
            avg_vol = hist['Volume'].mean()
            vol_ratio = recent_vol / avg_vol if avg_vol > 0 else 1
            
            if vol_ratio > 2:
                score_data['score'] += 5
                score_data['details'].append(f"📊 Volume {vol_ratio:.1f}x average")
            
            score_data['score'] = min(score_data['score'], 20)
            
        except Exception as e:
            score_data['details'].append(f"⚠️ Error: {e}")
        
        return score_data
    
    def _score_failed_breakout(self, ticker: str) -> Dict:
        """Check if this is a failed breakout resetting"""
        score_data = {'score': 0, 'details': []}
        
        try:
            from research.failed_breakout_detector import FailedBreakoutDetector
            
            detector = FailedBreakoutDetector()
            result = detector.detect_failed_breakout(ticker)
            
            if result:
                score_data['score'] = result.get('conviction_boost', 0)
                score_data['details'].append(f"🔄 Failed breakout: +{result['run_pct']:.0f}% → -{result['retracement_pct']:.0f}%")
                if result.get('insider_support'):
                    score_data['details'].append("💎 Insiders buying the dip!")
        
        except Exception as e:
            pass  # Failedbreakout is bonus, don't error out
        
        return score_data
    
    def _generate_verdict(self, score: int) -> str:
        """Generate actionable verdict"""
        if score >= 85:
            return "🔥 HUNT NOW - AISP-level setup"
        elif score >= 75:
            return "✅ STRONG BUY - High conviction"
        elif score >= 65:
            return "👍 BUY - Good setup"
        elif score >= 55:
            return "⏳ WATCHLIST - Wait for better entry"
        else:
            return "🚫 PASS - Insufficient conviction"
    
    def _suggest_timeframe(self, components: Dict) -> str:
        """Suggest trade timeframe"""
        catalyst_score = components.get('catalyst', {}).get('score', 0)
        
        if catalyst_score >= 10:
            return "SWING (1-4 weeks) - Catalyst play"
        else:
            return "POSITION (1-3 months) - Accumulation"
    
    def _identify_risks(self, components: Dict) -> List[str]:
        """Identify key risks"""
        risks = []
        
        sector_score = components.get('sector', {}).get('score', 0)
        if sector_score == 0:
            risks.append("Sector not rotating - may need patience")
        
        catalyst_score = components.get('catalyst', {}).get('score', 0)
        if catalyst_score == 0:
            risks.append("No visible catalyst - longer hold")
        
        insider_score = components.get('insider', {}).get('score', 0)
        if insider_score < 15:
            risks.append("Weak insider conviction - verify setup")
        
        return risks
    
    def scan_watchlist_unified(self, tickers: List[str]) -> List[Dict]:
        """
        Run unified conviction on entire watchlist
        Returns sorted by conviction score
        """
        results = []
        
        print(f"🐺 Running Wolf Intelligence on {len(tickers)} tickers...")
        
        for ticker in tickers:
            try:
                conviction = self.calculate_unified_conviction(ticker)
                results.append(conviction)
            except Exception as e:
                print(f"⚠️ {ticker}: {e}")
        
        # Sort by score
        results.sort(key=lambda x: x['total_score'], reverse=True)
        
        return results
    
    def generate_morning_report(self, tickers: List[str]) -> str:
        """
        Generate Monday morning report
        Top 5 targets with full breakdown
        """
        results = self.scan_watchlist_unified(tickers)
        
        report = []
        report.append("=" * 70)
        report.append("🐺 WOLF PACK MORNING INTELLIGENCE")
        report.append(f"📅 {datetime.now().strftime('%A, %B %d, %Y %I:%M %p')}")
        report.append("=" * 70)
        report.append("")
        
        # Top 5 targets
        top_targets = results[:5]
        
        for i, target in enumerate(top_targets, 1):
            report.append(f"\n{'='*70}")
            report.append(f"#{i} - {target['ticker']}: {target['total_score']:.0f}/100 - {target['verdict']}")
            report.append(f"{'='*70}")
            
            # Component breakdown
            for component, data in target['components'].items():
                score = data.get('score', 0)
                details = data.get('details', [])
                
                if score > 0 or details:
                    report.append(f"\n{component.upper()}: {score} points")
                    for detail in details:
                        report.append(f"  {detail}")
            
            report.append(f"\n⏱️  Timeframe: {target['timeframe']}")
            
            if target['risks']:
                report.append(f"\n⚠️  Risks:")
                for risk in target['risks']:
                    report.append(f"  • {risk}")
        
        report.append("\n" + "=" * 70)
        report.append("LLHR 🐺")
        report.append("=" * 70)
        
        return "\n".join(report)


if __name__ == "__main__":
    import sys
    
    # CLI for testing
    wolf = WolfIntelligence()
    
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
        conviction = wolf.calculate_unified_conviction(ticker)
        
        print(f"\n{'='*70}")
        print(f"{ticker}: {conviction['total_score']:.0f}/100 - {conviction['verdict']}")
        print(f"{'='*70}")
        
        for component, data in conviction['components'].items():
            score = data.get('score', 0)
            details = data.get('details', [])
            
            if score > 0 or details:
                print(f"\n{component.upper()}: {score} points")
                for detail in details:
                    print(f"  {detail}")
        
        print(f"\n⏱️  Timeframe: {conviction['timeframe']}")
        
        if conviction['risks']:
            print(f"\n⚠️  Risks:")
            for risk in conviction['risks']:
                print(f"  • {risk}")
    else:
        print("Usage: python wolf_intelligence.py TICKER")
