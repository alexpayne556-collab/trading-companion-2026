#!/usr/bin/env python3
"""
🐺 WOLF LEARNER - The System That Learns YOU
=============================================
Personal trading intelligence that evolves with every decision.

TRACKS:
- Signals you took vs skipped
- Outcomes of trades by signal source
- Your personal win rates per setup type
- Patterns in your best and worst trades

LEARNS:
- Which signals YOU win on
- Your optimal position sizing
- Time-of-day performance
- Sector strengths/weaknesses

ADAPTS:
- Weights future signals based on YOUR history
- Flags setups where you historically struggle
- Suggests position size based on your edge

Run: python wolf_learner.py analyze
     python wolf_learner.py profile
     python wolf_learner.py weight TICKER

AWOOOO 🐺
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics

# ============================================================
# CONFIGURATION
# ============================================================

class LearnerConfig:
    """Learner settings"""
    
    JOURNAL_FILE = "logs/trade_journal.jsonl"
    SIGNALS_SKIPPED_FILE = "logs/signals_skipped.jsonl"
    PROFILE_FILE = "logs/wolf_profile.json"
    
    # Minimum trades to establish edge
    MIN_TRADES_FOR_EDGE = 5
    
    # Weight decay - older trades matter less
    WEIGHT_DECAY_DAYS = 90
    
    # Signal source categories
    SIGNAL_SOURCES = [
        "insider_buy",
        "short_squeeze",
        "capitulation",
        "momentum",
        "laggard",
        "volume_spike",
        "pocket_pivot",
        "wolf_signal",
        "manual"
    ]
    
    # Sectors for sector analysis
    SECTORS = [
        "quantum", "nuclear", "ai_chips", "space",
        "crypto", "ev", "biotech", "voice_ai",
        "financials", "energy", "tech", "other"
    ]


# ============================================================
# TRADE JOURNAL INTERFACE
# ============================================================

class TradeJournalReader:
    """Read and parse trade journal entries"""
    
    def __init__(self):
        self.journal_file = Path(LearnerConfig.JOURNAL_FILE)
    
    def load_trades(self) -> List[dict]:
        """Load all trades from journal"""
        trades = []
        
        if not self.journal_file.exists():
            return trades
        
        with open(self.journal_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        trades.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        
        return trades
    
    def get_closed_trades(self) -> List[dict]:
        """Get only closed (completed) trades"""
        trades = self.load_trades()
        return [t for t in trades if t.get("status") == "closed"]
    
    def get_open_trades(self) -> List[dict]:
        """Get currently open positions"""
        trades = self.load_trades()
        return [t for t in trades if t.get("status") == "open"]


# ============================================================
# SIGNAL TRACKER
# ============================================================

class SignalTracker:
    """Track signals taken vs skipped"""
    
    def __init__(self):
        self.skipped_file = Path(LearnerConfig.SIGNALS_SKIPPED_FILE)
        self.skipped_file.parent.mkdir(exist_ok=True)
    
    def record_skip(self, ticker: str, signal_type: str, reason: str = ""):
        """Record a skipped signal"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker,
            "signal_type": signal_type,
            "reason": reason,
            "action": "skipped"
        }
        
        with open(self.skipped_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        print(f"📝 Recorded skip: {ticker} ({signal_type})")
    
    def load_skipped(self) -> List[dict]:
        """Load all skipped signals"""
        skipped = []
        
        if not self.skipped_file.exists():
            return skipped
        
        with open(self.skipped_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        skipped.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        
        return skipped
    
    def analyze_skips(self) -> Dict[str, dict]:
        """Analyze skipped signals - what would have happened?"""
        # This would fetch historical prices to see outcome
        # For now, return summary
        skipped = self.load_skipped()
        
        by_signal = defaultdict(list)
        for s in skipped:
            by_signal[s.get("signal_type", "unknown")].append(s)
        
        return {
            signal: {
                "count": len(items),
                "tickers": list(set(i["ticker"] for i in items))[:5]
            }
            for signal, items in by_signal.items()
        }


# ============================================================
# WOLF LEARNER - CORE ANALYTICS
# ============================================================

class WolfLearner:
    """Main learning engine - builds your profile"""
    
    def __init__(self):
        self.journal = TradeJournalReader()
        self.tracker = SignalTracker()
        self.profile_file = Path(LearnerConfig.PROFILE_FILE)
    
    # ========================================
    # ANALYSIS
    # ========================================
    
    def analyze_by_signal(self) -> Dict[str, dict]:
        """Analyze performance by signal source"""
        trades = self.journal.get_closed_trades()
        
        if not trades:
            return {}
        
        by_signal = defaultdict(list)
        
        for trade in trades:
            signal = trade.get("signal_source", "manual")
            pnl_pct = trade.get("pnl_percent", 0)
            by_signal[signal].append({
                "ticker": trade.get("ticker"),
                "pnl": pnl_pct,
                "hold_days": trade.get("hold_days", 0),
                "date": trade.get("close_date", trade.get("entry_date"))
            })
        
        results = {}
        
        for signal, signal_trades in by_signal.items():
            pnls = [t["pnl"] for t in signal_trades]
            wins = [p for p in pnls if p > 0]
            losses = [p for p in pnls if p <= 0]
            
            results[signal] = {
                "trades": len(signal_trades),
                "win_rate": len(wins) / len(pnls) * 100 if pnls else 0,
                "avg_win": statistics.mean(wins) if wins else 0,
                "avg_loss": statistics.mean(losses) if losses else 0,
                "avg_return": statistics.mean(pnls) if pnls else 0,
                "total_return": sum(pnls),
                "best_trade": max(pnls) if pnls else 0,
                "worst_trade": min(pnls) if pnls else 0,
                "expectancy": self._calc_expectancy(wins, losses),
                "edge_established": len(signal_trades) >= LearnerConfig.MIN_TRADES_FOR_EDGE
            }
        
        return results
    
    def analyze_by_sector(self) -> Dict[str, dict]:
        """Analyze performance by sector"""
        trades = self.journal.get_closed_trades()
        
        if not trades:
            return {}
        
        by_sector = defaultdict(list)
        
        for trade in trades:
            sector = trade.get("sector", "other")
            pnl = trade.get("pnl_percent", 0)
            by_sector[sector].append(pnl)
        
        results = {}
        
        for sector, pnls in by_sector.items():
            wins = [p for p in pnls if p > 0]
            
            results[sector] = {
                "trades": len(pnls),
                "win_rate": len(wins) / len(pnls) * 100 if pnls else 0,
                "avg_return": statistics.mean(pnls) if pnls else 0,
                "total_return": sum(pnls)
            }
        
        return results
    
    def analyze_by_time(self) -> Dict[str, dict]:
        """Analyze performance by time factors"""
        trades = self.journal.get_closed_trades()
        
        if not trades:
            return {}
        
        # By day of week
        by_day = defaultdict(list)
        # By month
        by_month = defaultdict(list)
        # By hold period
        by_hold = defaultdict(list)
        
        for trade in trades:
            pnl = trade.get("pnl_percent", 0)
            
            entry_date = trade.get("entry_date")
            if entry_date:
                try:
                    dt = datetime.fromisoformat(entry_date.replace("Z", "+00:00"))
                    by_day[dt.strftime("%A")].append(pnl)
                    by_month[dt.strftime("%B")].append(pnl)
                except Exception:
                    pass
            
            hold_days = trade.get("hold_days", 0)
            if hold_days <= 1:
                by_hold["intraday"].append(pnl)
            elif hold_days <= 5:
                by_hold["swing (1-5d)"].append(pnl)
            else:
                by_hold["position (5d+)"].append(pnl)
        
        return {
            "by_day": {
                day: {
                    "trades": len(pnls),
                    "win_rate": len([p for p in pnls if p > 0]) / len(pnls) * 100 if pnls else 0,
                    "avg_return": statistics.mean(pnls) if pnls else 0
                }
                for day, pnls in by_day.items()
            },
            "by_month": {
                month: {
                    "trades": len(pnls),
                    "avg_return": statistics.mean(pnls) if pnls else 0
                }
                for month, pnls in by_month.items()
            },
            "by_hold_period": {
                period: {
                    "trades": len(pnls),
                    "win_rate": len([p for p in pnls if p > 0]) / len(pnls) * 100 if pnls else 0,
                    "avg_return": statistics.mean(pnls) if pnls else 0
                }
                for period, pnls in by_hold.items()
            }
        }
    
    def _calc_expectancy(self, wins: List[float], losses: List[float]) -> float:
        """Calculate trading expectancy"""
        if not wins and not losses:
            return 0
        
        total = len(wins) + len(losses)
        win_rate = len(wins) / total
        loss_rate = len(losses) / total
        
        avg_win = statistics.mean(wins) if wins else 0
        avg_loss = abs(statistics.mean(losses)) if losses else 0
        
        # Expectancy = (Win Rate × Avg Win) - (Loss Rate × Avg Loss)
        return (win_rate * avg_win) - (loss_rate * avg_loss)
    
    # ========================================
    # PROFILE BUILDING
    # ========================================
    
    def build_profile(self) -> dict:
        """Build comprehensive trading profile"""
        trades = self.journal.get_closed_trades()
        
        if not trades:
            return {"error": "No closed trades found. Start trading and log results!"}
        
        signal_analysis = self.analyze_by_signal()
        sector_analysis = self.analyze_by_sector()
        time_analysis = self.analyze_by_time()
        skip_analysis = self.tracker.analyze_skips()
        
        # Find strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for signal, stats in signal_analysis.items():
            if stats["edge_established"]:
                if stats["win_rate"] >= 60 and stats["expectancy"] > 0:
                    strengths.append({
                        "type": "signal",
                        "name": signal,
                        "win_rate": stats["win_rate"],
                        "expectancy": stats["expectancy"]
                    })
                elif stats["win_rate"] < 45 or stats["expectancy"] < 0:
                    weaknesses.append({
                        "type": "signal",
                        "name": signal,
                        "win_rate": stats["win_rate"],
                        "expectancy": stats["expectancy"]
                    })
        
        for sector, stats in sector_analysis.items():
            if stats["trades"] >= LearnerConfig.MIN_TRADES_FOR_EDGE:
                if stats["win_rate"] >= 60:
                    strengths.append({
                        "type": "sector",
                        "name": sector,
                        "win_rate": stats["win_rate"]
                    })
                elif stats["win_rate"] < 45:
                    weaknesses.append({
                        "type": "sector",
                        "name": sector,
                        "win_rate": stats["win_rate"]
                    })
        
        # Calculate overall stats
        all_pnls = [t.get("pnl_percent", 0) for t in trades]
        all_wins = [p for p in all_pnls if p > 0]
        all_losses = [p for p in all_pnls if p <= 0]
        
        profile = {
            "generated": datetime.now().isoformat(),
            "total_trades": len(trades),
            
            "overall": {
                "win_rate": len(all_wins) / len(all_pnls) * 100 if all_pnls else 0,
                "avg_return": statistics.mean(all_pnls) if all_pnls else 0,
                "total_return": sum(all_pnls),
                "expectancy": self._calc_expectancy(all_wins, all_losses),
                "best_trade": max(all_pnls) if all_pnls else 0,
                "worst_trade": min(all_pnls) if all_pnls else 0,
                "profit_factor": abs(sum(all_wins) / sum(all_losses)) if all_losses and sum(all_losses) != 0 else 0
            },
            
            "by_signal": signal_analysis,
            "by_sector": sector_analysis,
            "by_time": time_analysis,
            "skipped_signals": skip_analysis,
            
            "strengths": sorted(strengths, key=lambda x: x.get("win_rate", 0), reverse=True),
            "weaknesses": sorted(weaknesses, key=lambda x: x.get("win_rate", 100)),
            
            "recommendations": self._generate_recommendations(
                signal_analysis, sector_analysis, time_analysis, strengths, weaknesses
            )
        }
        
        # Save profile
        self.profile_file.parent.mkdir(exist_ok=True)
        with open(self.profile_file, "w") as f:
            json.dump(profile, f, indent=2)
        
        return profile
    
    def _generate_recommendations(self, signals, sectors, time_data, strengths, weaknesses) -> List[str]:
        """Generate personalized recommendations"""
        recs = []
        
        # Signal recommendations
        for signal, stats in signals.items():
            if stats["edge_established"]:
                if stats["win_rate"] >= 70:
                    recs.append(f"🟢 LEAN INTO {signal.upper()}: {stats['win_rate']:.0f}% win rate - this is YOUR edge")
                elif stats["win_rate"] < 40:
                    recs.append(f"🔴 AVOID {signal.upper()}: Only {stats['win_rate']:.0f}% win rate - not your setup")
        
        # Hold period recommendations
        if "by_hold_period" in time_data:
            hold_stats = time_data["by_hold_period"]
            best_hold = max(hold_stats.items(), key=lambda x: x[1].get("win_rate", 0)) if hold_stats else None
            if best_hold and best_hold[1]["trades"] >= 5:
                recs.append(f"⏱️ Your best hold period: {best_hold[0]} ({best_hold[1]['win_rate']:.0f}% win rate)")
        
        # Sector recommendations
        for sector, stats in sectors.items():
            if stats["trades"] >= 5:
                if stats["win_rate"] >= 70:
                    recs.append(f"🎯 SECTOR STRENGTH: {sector} ({stats['win_rate']:.0f}% win rate)")
        
        # General recommendations
        if weaknesses:
            worst = weaknesses[0]
            recs.append(f"⚠️ Consider reducing exposure to {worst['name']} setups")
        
        return recs
    
    # ========================================
    # SIGNAL WEIGHTING
    # ========================================
    
    def get_signal_weight(self, signal_type: str) -> float:
        """
        Get personalized weight for a signal type
        Returns 0.0 - 2.0 (1.0 is neutral)
        """
        profile = self._load_profile()
        
        if not profile or "by_signal" not in profile:
            return 1.0  # Neutral weight
        
        signal_stats = profile["by_signal"].get(signal_type)
        
        if not signal_stats or not signal_stats.get("edge_established"):
            return 1.0  # Not enough data
        
        win_rate = signal_stats["win_rate"]
        expectancy = signal_stats["expectancy"]
        
        # Weight based on win rate
        # 50% = 1.0, 60% = 1.2, 70% = 1.4, 40% = 0.8, etc.
        weight = 1.0 + (win_rate - 50) / 50
        
        # Adjust for expectancy
        if expectancy > 5:
            weight *= 1.1
        elif expectancy < -5:
            weight *= 0.9
        
        # Clamp to reasonable range
        return max(0.2, min(2.0, weight))
    
    def weight_signals(self, signals: List[dict]) -> List[dict]:
        """
        Apply personal weights to a list of signals
        """
        weighted = []
        
        for signal in signals:
            signal_type = signal.get("signal_type", "manual")
            base_confidence = signal.get("confidence", 50)
            
            weight = self.get_signal_weight(signal_type)
            adjusted_confidence = base_confidence * weight
            
            weighted_signal = signal.copy()
            weighted_signal["original_confidence"] = base_confidence
            weighted_signal["personal_weight"] = weight
            weighted_signal["adjusted_confidence"] = min(100, adjusted_confidence)
            weighted_signal["weight_reason"] = self._get_weight_reason(signal_type, weight)
            
            weighted.append(weighted_signal)
        
        # Sort by adjusted confidence
        weighted.sort(key=lambda x: x["adjusted_confidence"], reverse=True)
        
        return weighted
    
    def _get_weight_reason(self, signal_type: str, weight: float) -> str:
        """Explain why weight was applied"""
        if weight > 1.2:
            return f"⬆️ YOU excel at {signal_type} setups"
        elif weight > 1.0:
            return f"↗️ Slight edge on {signal_type}"
        elif weight < 0.8:
            return f"⬇️ YOU struggle with {signal_type} - caution"
        elif weight < 1.0:
            return f"↘️ Below average on {signal_type}"
        else:
            return "➡️ Neutral - no established edge yet"
    
    def _load_profile(self) -> Optional[dict]:
        """Load saved profile"""
        if self.profile_file.exists():
            with open(self.profile_file) as f:
                return json.load(f)
        return None
    
    # ========================================
    # POSITION SIZING
    # ========================================
    
    def suggest_position_size(self, signal_type: str, base_size: float = 1.0) -> dict:
        """
        Suggest position size based on your edge
        base_size: Your normal position size (1.0 = full position)
        """
        profile = self._load_profile()
        weight = self.get_signal_weight(signal_type)
        
        suggested_size = base_size * weight
        
        # Get stats for explanation
        stats = None
        if profile and "by_signal" in profile:
            stats = profile["by_signal"].get(signal_type)
        
        return {
            "signal_type": signal_type,
            "base_size": base_size,
            "personal_weight": weight,
            "suggested_size": round(suggested_size, 2),
            "explanation": self._size_explanation(weight, stats)
        }
    
    def _size_explanation(self, weight: float, stats: Optional[dict]) -> str:
        """Explain position size suggestion"""
        if not stats or not stats.get("edge_established"):
            return "Insufficient data - using base size. Trade small until edge is established."
        
        if weight >= 1.5:
            return f"Strong edge! ({stats['win_rate']:.0f}% win rate). Consider full or oversized position."
        elif weight >= 1.2:
            return f"Good edge ({stats['win_rate']:.0f}% win rate). Full position appropriate."
        elif weight >= 0.8:
            return f"Neutral ({stats['win_rate']:.0f}% win rate). Normal position size."
        else:
            return f"Weak edge ({stats['win_rate']:.0f}% win rate). Consider half position or skip."


# ============================================================
# CLI & DISPLAY
# ============================================================

def display_profile(profile: dict):
    """Display trading profile"""
    print("=" * 60)
    print("🐺 YOUR WOLF PROFILE")
    print("=" * 60)
    
    if "error" in profile:
        print(f"\n{profile['error']}")
        return
    
    overall = profile["overall"]
    
    print(f"\n📊 OVERALL PERFORMANCE ({profile['total_trades']} trades)")
    print("-" * 40)
    print(f"  Win Rate:      {overall['win_rate']:.1f}%")
    print(f"  Avg Return:    {overall['avg_return']:+.2f}%")
    print(f"  Total Return:  {overall['total_return']:+.1f}%")
    print(f"  Expectancy:    {overall['expectancy']:.2f}")
    print(f"  Profit Factor: {overall['profit_factor']:.2f}")
    print(f"  Best Trade:    {overall['best_trade']:+.1f}%")
    print(f"  Worst Trade:   {overall['worst_trade']:+.1f}%")
    
    # By signal type
    print(f"\n📈 BY SIGNAL TYPE")
    print("-" * 40)
    
    by_signal = profile.get("by_signal", {})
    for signal, stats in sorted(by_signal.items(), key=lambda x: x[1]["win_rate"], reverse=True):
        edge_marker = "✓" if stats["edge_established"] else "○"
        print(f"  {edge_marker} {signal:15s} | {stats['trades']:3d} trades | "
              f"Win: {stats['win_rate']:5.1f}% | Avg: {stats['avg_return']:+6.2f}%")
    
    # Strengths
    if profile.get("strengths"):
        print(f"\n💪 YOUR STRENGTHS")
        print("-" * 40)
        for s in profile["strengths"][:5]:
            print(f"  ✅ {s['type'].upper()}: {s['name']} ({s['win_rate']:.0f}% win rate)")
    
    # Weaknesses
    if profile.get("weaknesses"):
        print(f"\n⚠️ YOUR WEAKNESSES")
        print("-" * 40)
        for w in profile["weaknesses"][:5]:
            print(f"  ❌ {w['type'].upper()}: {w['name']} ({w['win_rate']:.0f}% win rate)")
    
    # Recommendations
    if profile.get("recommendations"):
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 40)
        for rec in profile["recommendations"]:
            print(f"  {rec}")
    
    print()
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="🐺 Wolf Learner - Personal trading intelligence"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze trading performance")
    analyze_parser.add_argument("--signal", type=str, help="Analyze specific signal type")
    analyze_parser.add_argument("--sector", type=str, help="Analyze specific sector")
    
    # Profile command
    profile_parser = subparsers.add_parser("profile", help="Build/view trading profile")
    profile_parser.add_argument("--refresh", action="store_true", help="Force rebuild profile")
    
    # Weight command
    weight_parser = subparsers.add_parser("weight", help="Get signal weight")
    weight_parser.add_argument("signal_type", type=str, help="Signal type to weight")
    
    # Size command
    size_parser = subparsers.add_parser("size", help="Get position size suggestion")
    size_parser.add_argument("signal_type", type=str, help="Signal type")
    size_parser.add_argument("--base", type=float, default=1.0, help="Base position size")
    
    # Skip command
    skip_parser = subparsers.add_parser("skip", help="Record a skipped signal")
    skip_parser.add_argument("ticker", type=str, help="Ticker symbol")
    skip_parser.add_argument("signal_type", type=str, help="Signal type")
    skip_parser.add_argument("--reason", type=str, default="", help="Reason for skip")
    
    # Skips analysis
    skips_parser = subparsers.add_parser("skips", help="Analyze skipped signals")
    
    args = parser.parse_args()
    
    learner = WolfLearner()
    
    if args.command == "analyze":
        if args.signal:
            analysis = learner.analyze_by_signal()
            if args.signal in analysis:
                stats = analysis[args.signal]
                print(f"\n📊 {args.signal.upper()} Analysis:")
                print(f"  Trades: {stats['trades']}")
                print(f"  Win Rate: {stats['win_rate']:.1f}%")
                print(f"  Avg Return: {stats['avg_return']:+.2f}%")
                print(f"  Expectancy: {stats['expectancy']:.2f}")
            else:
                print(f"No data for signal type: {args.signal}")
        elif args.sector:
            analysis = learner.analyze_by_sector()
            if args.sector in analysis:
                stats = analysis[args.sector]
                print(f"\n📊 {args.sector.upper()} Sector Analysis:")
                print(f"  Trades: {stats['trades']}")
                print(f"  Win Rate: {stats['win_rate']:.1f}%")
                print(f"  Avg Return: {stats['avg_return']:+.2f}%")
            else:
                print(f"No data for sector: {args.sector}")
        else:
            # Full analysis
            print("Building analysis...")
            profile = learner.build_profile()
            display_profile(profile)
    
    elif args.command == "profile":
        profile = learner.build_profile()
        display_profile(profile)
    
    elif args.command == "weight":
        weight = learner.get_signal_weight(args.signal_type)
        print(f"\n🎯 Signal Weight for {args.signal_type.upper()}")
        print(f"  Weight: {weight:.2f}x")
        if weight > 1.0:
            print(f"  → This is a strength for you")
        elif weight < 1.0:
            print(f"  → This is a weakness for you")
        else:
            print(f"  → Neutral (not enough data)")
    
    elif args.command == "size":
        suggestion = learner.suggest_position_size(args.signal_type, args.base)
        print(f"\n📏 Position Size Suggestion")
        print(f"  Signal Type: {suggestion['signal_type']}")
        print(f"  Base Size: {suggestion['base_size']:.2f}")
        print(f"  Weight: {suggestion['personal_weight']:.2f}x")
        print(f"  Suggested Size: {suggestion['suggested_size']:.2f}")
        print(f"  {suggestion['explanation']}")
    
    elif args.command == "skip":
        tracker = SignalTracker()
        tracker.record_skip(args.ticker.upper(), args.signal_type, args.reason)
    
    elif args.command == "skips":
        tracker = SignalTracker()
        analysis = tracker.analyze_skips()
        
        if analysis:
            print("\n📋 Skipped Signals Analysis")
            print("-" * 40)
            for signal, data in analysis.items():
                print(f"  {signal}: {data['count']} skipped")
                print(f"    Recent: {', '.join(data['tickers'])}")
        else:
            print("No skipped signals recorded.")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
