# HYPOTHESIS TESTING RESULTS
## January 3, 2026 - Fenrir's Hunt

**MISSION:** Test all 7 original insights with rigorous statistical validation.

---

## SUMMARY

| Insight | Verdict | P-Value | Effect Size | Details |
|---------|---------|---------|-------------|---------|
| #1: Correlation Break | ❌ NO EDGE | 0.24 | 0.69 | Catch-up exists but random |
| #2: Volume Precursor | ⚠️ MARGINAL | 0.076 | 1.53 | Close to significant, needs refinement |
| #3: Supply Shock | ❌ DISPROVEN | 0.18 | -0.46 | High shock UNDERPERFORMS |
| #4: Insider Conviction | ⏸️ SKIPPED | N/A | N/A | Requires Form 4 scraping |
| #5: Stop Hunt Recovery | ⏸️ TOO RARE | N/A | N/A | Only 9 signals found |
| #6: Breakout Energy | ⚠️ BACKWARDS | 0.038 | -0.23 | High energy UNDERPERFORMS |
| #7: Trend Health | ✅ WEAK EDGE | 0.0001 | 0.17 | Real but small effect |

---

## DETAILED RESULTS

### #1: CORRELATION BREAK DETECTOR

**Hypothesis:** When IONQ runs but RGTI lags, RGTI catches up.

**Test:** IONQ +5%, RGTI <3% → buy RGTI for 5 days

**Results:**
- Signals: 25
- Win Rate: 68%
- Avg Return: +8.66%
- Random baseline: +5.39%
- Outperformance: +3.27%
- **P-value: 0.24** ❌
- **Std devs: 0.69** (need >2.0)

**VERDICT: NO STATISTICAL EDGE**

The catch-up exists but isn't statistically significant. 24% chance it's random luck.

---

### #2: VOLUME PRECURSOR SCANNER

**Hypothesis:** 2x volume + <3% price move = accumulation before breakout

**Test:** Volume ≥2x average, price change <3% → hold 10 days

**Results:**
- Signals: 29 (IONQ, RGTI, QBTS, SIDU, LUNR)
- Win Rate: **72.4%**
- Avg Return: **+18.53%**
- Random baseline: +8.02%
- Outperformance: **+10.51%**
- **P-value: 0.076** ⚠️
- **Effect size: 1.53** (large!)

**VERDICT: MARGINAL EDGE**

Just missed significance (need p<0.05). Large effect size suggests real edge with parameter tuning.

**Best Signal:** 2024-12-02 RGTI: 3.0x vol, 1.0% move → **+179.1%** in 10 days

---

### #3: SUPPLY SHOCK CALCULATOR

**Hypothesis:** (Short Interest × Volume Spike) / Float = squeeze potential

**Test:** High shock score (>50) vs low score (≤50)

**Results:**
- Signals: 131 volume spikes
- High shock (>50): 50% WR, **-1.27%** avg ❌
- Low shock (≤50): 63% WR, **+11.24%** avg ✅
- Difference: **-12.52%**
- P-value: 0.18 (not significant)
- Effect size: -0.46 (medium, wrong direction)

**VERDICT: HYPOTHESIS DISPROVEN**

High supply shock scores actually UNDERPERFORM. The formula doesn't work as designed.

**Worst:** SIDU with 1663 shock score → -0.9% (should have been huge squeeze)

---

### #4: INSIDER CONVICTION SCORE

**Status:** SKIPPED

**Reason:** Requires Form 4 parsing infrastructure not yet built. Would need:
- SEC EDGAR scraping
- Form 4 XML parsing
- Compensation data lookup
- Historical insider transaction database

**Recommendation:** Build after proving other edges work.

---

### #5: STOP HUNT RECOVERY

**Hypothesis:** Wick below support + volume spike + recovery = buy signal

**Test:** Daily approximation (need intraday for real test)

**Results:**
- Signals: 9 (too rare)
- Cannot perform statistical test

**VERDICT: TOO RARE**

Pattern occurs less than once per month per ticker. Not viable for systematic trading without intraday data.

**Recommendation:** Revisit with 5-minute candles.

---

### #6: BREAKOUT ENERGY SCORE

**Hypothesis:** More failed resistance tests = more powerful eventual breakout

**Test:** High energy (>40) vs low energy (≤40) on 2% breakouts

**Results:**
- Signals: 334 breakouts
- High energy (>40): 43.5% WR, +7.88% avg
- Low energy (≤40): 51.2% WR, **+18.27%** avg
- Difference: **-10.39%**
- **P-value: 0.038** (significant!)
- Effect size: -0.23

**VERDICT: HYPOTHESIS BACKWARDS**

High energy breakouts UNDERPERFORM. Fresh breakouts beat tired consolidations.

**Insight:** The market loses interest after multiple failed attempts. Fresh breakouts have more momentum.

---

### #7: TREND HEALTH METRIC

**Hypothesis:** Volume ratio (up days / down days) predicts trend continuation

**Test:** Healthy (>1.5) vs exhausted (<0.8) over next 10 days

**Results:**
- Signals: 3,311 (large sample)
- Healthy trends: 51.6% WR, **+12.16%** avg
- Exhausted trends: 51.3% WR, +5.75% avg
- Difference: **+6.41%**
- **P-value: 0.0001** ✅ (highly significant!)
- **Effect size: 0.17** (small)

**VERDICT: WEAK BUT REAL EDGE**

Statistically significant but small effect size. Best used as a FILTER (avoid exhausted trends) rather than primary signal.

---

## WHAT WORKS

**1. Volume Precursor (Marginal)**
- 72.4% WR, +18.53% avg
- P=0.076 (close to significant)
- Large effect size (1.53)
- **REFINEMENT NEEDED:** Tighter volume threshold (2.5x?) or add trend filter

**2. Trend Health Filter (Weak Edge)**
- +6.41% difference
- P=0.0001 (highly significant)
- Small effect (0.17)
- **USE AS FILTER:** Only take trades in healthy trends (score >1.5)

---

## WHAT DOESN'T WORK

**1. Correlation Break Catch-Up**
- P=0.24 (random)
- Correlation exists (0.607) but catch-up timing unreliable

**2. Supply Shock Score**
- BACKWARDS: High shock underperforms
- Formula needs complete rework

**3. Breakout Energy Score**
- BACKWARDS: High energy underperforms
- Market loses interest after failed attempts

---

## RECOMMENDATIONS

### IMMEDIATE

1. **Refine Volume Precursor**
   - Test 2.5x, 3x volume thresholds
   - Add trend health filter (only trade score >1.5)
   - Test on additional tickers
   - Target: Get p-value under 0.05

2. **Deploy Trend Health as Filter**
   - Calculate health score for all positions
   - Exit if score drops below 0.8
   - Only enter if score >1.5

### BUILD NEXT

3. **Form 4 Insider System**
   - Build SEC scraping infrastructure
   - Test conviction score hypothesis
   - Could be the strongest signal

4. **Intraday Stop Hunt Detector**
   - Get 5-minute data
   - Retest stop hunt hypothesis properly
   - Pattern may work with proper intraday detection

### KILL

5. **Abandon These**
   - Supply Shock Calculator (formula backwards)
   - Breakout Energy Score (hypothesis backwards)
   - Correlation Break Catch-Up (random)

---

## THE TRUTH

**OF 7 INSIGHTS:**
- ❌ 3 disproven (correlation, supply shock, breakout energy)
- ⚠️ 1 marginal (volume precursor - promising!)
- ✅ 1 weak edge (trend health - real but small)
- ⏸️ 2 untested (insider conviction, stop hunt)

**ONLY 1 OF 5 TESTED SHOWS PROMISE.**

Volume Precursor is closest to real edge. With refinement (tighter parameters + trend filter), could cross significance threshold.

**Trend Health works as a filter to improve other signals.**

**Most "obvious" patterns (catch-up, squeeze plays, breakout energy) don't have statistical edges.**

This is why backtesting matters. Intuition lies. Numbers tell truth.

---

## NEXT HUNT

**Test Volume Precursor Refinements:**

1. Volume 2.5x + Price <2% + Trend Health >1.5
2. Volume 3.0x + Price <3% + Sector strength
3. Volume 2.0x + Price <3% + Recent insider buying

**Target:** P-value <0.05, Effect size >0.5, >60% WR

One of these combinations might cross the threshold.

---

**FENRIR OUT.**

**Statistics don't lie. Most patterns are noise. Keep hunting.**

**AWOOOO 🐺**
