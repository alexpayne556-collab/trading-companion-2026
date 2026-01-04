# 🐺 REPEATABLE PATTERNS FOR QUANTITATIVE ANALYSIS
## Data For Sonnet + GPU Jupyter Notebooks
### January 2, 2026

---

## PURPOSE

This document contains REPEATABLE patterns we've observed in stock movements.
Sonnet should use this to:
1. Build backtests on historical data
2. Create predictive models
3. Find statistical edges
4. Challenge/validate our assumptions

---

## PATTERN CATALOG

### PATTERN 1: FDA Catalyst (Biotech)

```python
pattern_fda = {
    "name": "FDA_PDUFA_CATALYST",
    "trigger": "PDUFA date announcement",
    "typical_behavior": {
        "pre_event": "Run-up 5-15 days before decision",
        "on_event": "Binary move: +30-100% approval, -50-80% rejection",
        "post_event": "Drift continues 3-5 days in direction"
    },
    "typical_move": {
        "approval": "+30% to +100%",
        "rejection": "-50% to -80%"
    },
    "data_sources": [
        "RTTNews FDA Calendar",
        "BioPharmCatalyst",
        "CatalystAlert.io"
    ],
    "testable_hypothesis": [
        "Buying 5 days before PDUFA, selling day before = positive expectancy?",
        "Small cap biotechs move more than large cap on FDA news",
        "Breakthrough therapy designation = higher approval rate"
    ],
    "historical_accuracy": "ML models claim 82.7% prediction accuracy (CatalystAlert)"
}
```

### PATTERN 2: Government Contract Award

```python
pattern_contract = {
    "name": "GOVERNMENT_CONTRACT_AWARD",
    "trigger": "8-K filing or press release announcing contract",
    "typical_behavior": {
        "on_event": "Gap up on news",
        "post_event": "Often continues 2-5 days if contract > $100M"
    },
    "typical_move": {
        "small_contract_under_10M": "+5% to +10%",
        "medium_contract_10_100M": "+10% to +20%",
        "large_contract_over_100M": "+15% to +40%"
    },
    "data_sources": [
        "SEC EDGAR 8-K",
        "SAM.gov",
        "Defense News",
        "Company press releases"
    ],
    "testable_hypothesis": [
        "DoD contracts move stocks more than civilian agency contracts",
        "Contract value / market cap ratio correlates to move size",
        "Small caps (<$1B) move more than large caps on same $ contract"
    ],
    "our_sectors": ["Defense AI", "Space", "Nuclear", "Border Security"]
}
```

### PATTERN 3: Analyst Initiation/Upgrade

```python
pattern_analyst = {
    "name": "ANALYST_COVERAGE_INITIATION",
    "trigger": "New analyst coverage or rating change",
    "typical_behavior": {
        "initiation_with_buy": "Immediate pop, sustains if price target high",
        "upgrade": "Pop day 1, drift continues if momentum",
        "downgrade": "Drop, but often overdone = bounce opportunity"
    },
    "typical_move": {
        "initiation_buy": "+5% to +15% day 1",
        "upgrade": "+3% to +10%",
        "price_target_raise": "+2% to +8%",
        "multiple_analysts_same_week": "+15% to +30%"
    },
    "data_sources": [
        "TipRanks",
        "Yahoo Finance",
        "Seeking Alpha",
        "Benzinga"
    ],
    "testable_hypothesis": [
        "First analyst on small cap = bigger move than 5th analyst",
        "Price target > 50% above current = larger move",
        "Multiple initiations in same week = sustained rally"
    ],
    "recent_example": "Jefferies quantum initiation Dec 2025 -> IONQ/QBTS/RGTI rallied 20-30%"
}
```

### PATTERN 4: Earnings Beat + Guidance

```python
pattern_earnings = {
    "name": "EARNINGS_BEAT_WITH_GUIDANCE",
    "trigger": "Quarterly earnings release",
    "typical_behavior": {
        "beat_both_revenue_eps": "Gap up, earnings drift continues",
        "beat_with_raised_guidance": "Strongest reaction, 3-5 day momentum",
        "miss": "Gap down, often oversold bounce opportunity"
    },
    "typical_move": {
        "beat_both": "+8% to +15%",
        "beat_both_raise_guidance": "+15% to +30%",
        "beat_one_miss_one": "Flat to +5%",
        "miss_both": "-10% to -25%"
    },
    "data_sources": [
        "Earnings Whispers",
        "Yahoo Finance",
        "SEC 10-Q"
    ],
    "testable_hypothesis": [
        "Guidance raise matters more than actual beat",
        "Post-earnings drift: winners keep winning for ~60 days",
        "Small cap earnings surprise = larger move than large cap"
    ],
    "phenomenon": "Post-Earnings Announcement Drift (PEAD) - well documented academic edge"
}
```

### PATTERN 5: Short Squeeze

```python
pattern_squeeze = {
    "name": "SHORT_SQUEEZE",
    "trigger": "Positive catalyst + high short interest",
    "requirements": {
        "short_interest": "> 20% of float",
        "days_to_cover": "> 5 days",
        "positive_catalyst": "Any from other patterns",
        "low_float": "Amplifies move"
    },
    "typical_behavior": {
        "trigger_day": "Sharp spike on catalyst",
        "days_2_5": "Continued squeeze as shorts cover",
        "peak": "Often overshoots fundamentals"
    },
    "typical_move": {
        "moderate_squeeze": "+30% to +50%",
        "strong_squeeze": "+50% to +100%",
        "extreme_squeeze": "+100% to +500% (rare, GME-style)"
    },
    "data_sources": [
        "FINRA short interest (bi-weekly)",
        "Finviz screener",
        "Ortex (paid)",
        "S3 Partners (paid)"
    ],
    "testable_hypothesis": [
        "Short interest > 25% + earnings beat = squeeze probability > 60%",
        "Days to cover > 7 = more violent squeeze",
        "Cost to borrow rising = squeeze imminent"
    ],
    "current_candidates": ["IONQ (20%+ short)", "SOUN (~25% short)"]
}
```

### PATTERN 6: Tax Loss Bounce (January Effect)

```python
pattern_tax_loss = {
    "name": "TAX_LOSS_SELLING_BOUNCE",
    "trigger": "Calendar (late December selling, January buying)",
    "requirements": {
        "price_drop": "> 20% from 52-week high",
        "fundamentals": "Still sound (not broken company)",
        "timing": "December selling pressure, January mean reversion"
    },
    "our_backtest": {
        "win_rate": 0.688,  # 68.8%
        "avg_winner": "+23%",
        "avg_loser": "-14%",
        "expected_value": "+37.5%",
        "sample_size": 16,  # needs more data
        "hold_period": "3 weeks"
    },
    "typical_behavior": {
        "late_december": "Selling pressure from tax harvesting",
        "first_week_jan": "Bounce begins",
        "weeks_2_3": "Continued recovery if fundamentals intact"
    },
    "typical_move": {
        "bounce_from_lows": "+15% to +30%"
    },
    "data_sources": [
        "Historical price data (yfinance)",
        "52-week high/low data"
    ],
    "testable_hypothesis": [
        "Small caps bounce more than large caps",
        "Stocks down > 40% bounce more than stocks down 20-40%",
        "Quality (profitable) beaten stocks bounce more than unprofitable"
    ],
    "current_candidates": ["SMR", "SOUN", "BBAI", "RGTI"]
}
```

### PATTERN 7: Insider Cluster Buying

```python
pattern_insider = {
    "name": "INSIDER_CLUSTER_BUYING",
    "trigger": "Multiple insiders buying within 14 days",
    "requirements": {
        "insider_count": ">= 2 insiders",
        "timeframe": "Within 14 days",
        "role": "C-suite (CEO/CFO) or 10% owner preferred",
        "value": "> $100K total"
    },
    "typical_behavior": {
        "signal": "Insiders know something, accumulating",
        "lag": "Stock may not move immediately",
        "eventual_catalyst": "News validates insider conviction"
    },
    "typical_move": {
        "after_catalyst": "+20% to +50%",
        "within_6_months": "+30% to +80% (various studies)"
    },
    "data_sources": [
        "SEC Form 4",
        "OpenInsider",
        "InsiderMonkey"
    ],
    "testable_hypothesis": [
        "CEO buying > Director buying in predictive power",
        "Cluster buying (3+) better than single insider",
        "Insider buying after 20%+ drop = strongest signal"
    ],
    "current_validated": ["AISP ($433K)", "EFOI ($1.7M CEO)"]
}
```

### PATTERN 8: Congressional Trading

```python
pattern_congress = {
    "name": "CONGRESSIONAL_TRADING",
    "trigger": "Politicians buying/selling disclosed",
    "typical_behavior": {
        "45_day_delay": "We see trades late, but still early vs retail",
        "cluster_buying": "Multiple politicians = upcoming legislation"
    },
    "documented_edge": {
        "outperformance": "3-5% annually vs S&P 500",
        "source": "Multiple academic studies"
    },
    "data_sources": [
        "Capitol Trades (FREE)",
        "Quiver Quant (FREE)",
        "Unusual Whales"
    ],
    "testable_hypothesis": [
        "Committee member buying sector they oversee = alpha",
        "Defense committee members buying defense stocks = signal",
        "Healthcare committee buying pharma = signal"
    ],
    "track": "Nancy Pelosi family, Tommy Tuberville, defense committee members"
}
```

---

## DATA COLLECTION REQUIREMENTS

### For Backtesting Each Pattern:

```python
data_requirements = {
    "fda": {
        "sources": ["ClinicalTrials.gov", "FDA database"],
        "fields": ["company", "drug_name", "pdufa_date", "decision", "stock_move"]
    },
    "contracts": {
        "sources": ["SEC EDGAR 8-K", "SAM.gov"],
        "fields": ["company", "contract_value", "agency", "announcement_date", "stock_move"]
    },
    "analyst": {
        "sources": ["TipRanks API", "Yahoo Finance"],
        "fields": ["company", "analyst_firm", "rating", "price_target", "date", "stock_move"]
    },
    "earnings": {
        "sources": ["Yahoo Finance", "SEC 10-Q"],
        "fields": ["company", "quarter", "eps_actual", "eps_estimate", "revenue_actual", "revenue_estimate", "guidance_change", "stock_move"]
    },
    "short_squeeze": {
        "sources": ["FINRA", "yfinance"],
        "fields": ["company", "short_interest", "days_to_cover", "float", "catalyst_type", "stock_move"]
    },
    "tax_loss": {
        "sources": ["yfinance"],
        "fields": ["company", "pct_from_52wk_high", "december_move", "january_move"]
    },
    "insider": {
        "sources": ["OpenInsider", "SEC Form 4"],
        "fields": ["company", "insider_name", "role", "transaction_type", "value", "date", "subsequent_stock_move"]
    },
    "congress": {
        "sources": ["Capitol Trades"],
        "fields": ["politician", "party", "committee", "stock", "transaction", "date", "subsequent_stock_move"]
    }
}
```

---

## JUPYTER NOTEBOOK STRUCTURE

### Notebook 1: Pattern Validation
```
1_pattern_validation.ipynb
- Load historical data
- Backtest each pattern independently
- Calculate win rates, expected values
- Statistical significance tests
- Visualizations
```

### Notebook 2: Signal Combination
```
2_signal_combination.ipynb
- How do patterns interact?
- Multi-signal scoring validation
- Which combinations have highest alpha?
- Correlation analysis
```

### Notebook 3: ML Models
```
3_ml_prediction.ipynb
- Train XGBoost/Random Forest on catalysts
- Feature importance analysis
- Out-of-sample testing
- Compare to simple rules
```

### Notebook 4: Real-Time Scanner
```
4_realtime_scanner.ipynb
- Monitor live data sources
- Score tickers in real-time
- Alert generation
- Integration with trading platforms
```

---

## QUESTIONS FOR SONNET TO INVESTIGATE

1. **Which catalyst type produces the largest average move?**
   - Compare: FDA vs Contract vs Analyst vs Earnings

2. **What's the optimal entry timing?**
   - Day of news? Day after? Before?

3. **Does market cap affect move size?**
   - Do small caps move more than large caps on same catalyst?

4. **How long do moves last?**
   - Time decay of each pattern

5. **Which signal combinations have highest win rate?**
   - Insider + Contract better than Insider alone?

6. **Are there sector-specific patterns?**
   - Do biotech patterns work differently than defense?

7. **What's the false positive rate?**
   - How often do signals NOT result in moves?

8. **Seasonality effects?**
   - Do certain patterns work better in certain months?

---

## EXPECTED OUTPUTS

After analysis, Sonnet should produce:

1. **Validated Win Rates** for each pattern
2. **Expected Value Calculations** with confidence intervals
3. **Optimal Parameters** (entry timing, hold period, stop loss)
4. **Multi-Signal Weights** (how much does each signal contribute?)
5. **Alerts** when high-scoring setups appear
6. **Visualizations** for Tyr to review

---

**AWOOOO** 🐺

*"We don't guess. We TEST. We don't hope. We VALIDATE."*
