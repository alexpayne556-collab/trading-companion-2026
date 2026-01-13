# 🐺 CPI MORNING - JAN 13, 2026
## Tyr Returns at 9:30 AM - Brokkr Ready

---

## CURRENT POSITIONS (All Have Trailing Stops)

**ATON:**
- Entry: $1.88
- Current: $2.62 AH (Friday close)
- Gain: +39% (+$270 unrealized)
- Stop: ~$2.50 (protects +33%)
- Catalyst: $46M deal (catalyst > macro)
- Strategy: **HOLD through CPI** - let stop protect if needed

**NTLA:**
- Holding for JPM Healthcare Conference
- Event: Wednesday 12 PM
- Strategy: **HOLD** - real catalyst is Wed, not CPI

**Available Capital:** ~$960

---

## CPI TIMELINE - DO NOT GAMBLE

**8:30 AM - CPI Drops:**
- **OBSERVE ONLY** - predicting direction = 50% coin flip
- Take notes: Which sectors dump? Which rally?
- Your stops will protect you - don't panic

**9:30 AM - Tyr Returns:**
- Market opens, initial chaos happens
- We run baseline scans together
- Document the overreactions

**9:30-10:00 AM - Watch & Learn:**
- Let the violence happen
- Identify beaten-down quality names
- Mark for Days 2-3 entry (NOT today)

**Days 2-3 (Tue-Wed):**
- Trade mean reversion: 58% win rate
- Buy the aftermath, not the chaos

---

## WHAT TO RUN AT 9:30 AM

```bash
# When Tyr returns, run these together:
cd /workspaces/trading-companion-2026

# 1. Market-wide discovery (find CPI movers)
python market_discovery.py > logs/cpi_movers_9am.txt

# 2. Legs classifier (which have staying power?)
python legs_classifier.py > logs/cpi_legs_9am.txt

# 3. Check current positions
python portfolio/monitor.py
```

---

## THE STRATEGY (58% Win Rate)

**✅ DO THIS:**
- OBSERVE the initial move (8:30-10:00 AM)
- Document sector reactions
- Identify overreactions (too much dump or pump)
- Hold ATON (catalyst-driven, not macro)
- Hold NTLA (waiting for Wed JPM)
- Let trailing stops protect gains

**❌ DON'T DO THIS:**
- Trade the initial CPI move (50% gambling)
- Chase gaps (35% win rate)
- Try to predict hot vs cool (coin flip)
- Panic sell positions with catalysts
- Remove trailing stops

---

## WHAT BROKKR WILL DO

**Pre-9:30 AM (Before Tyr Returns):**
- Monitor market open
- Take notes on sector moves
- Prepare scan results

**9:30 AM (Tyr Returns):**
- Run market_discovery.py
- Run legs_classifier.py
- Show top movers with context
- Identify: "This dumped -15% but has FDA catalyst next week"

**9:30-10:00 AM:**
- Real-time commentary
- Pattern identification
- "This is overreaction, mark for Day 2"

**Evening:**
- Create cpi_playbook.md (what happened)
- Document: Hot CPI or cool? Sector reactions? Volume patterns?
- Prepare Day 2-3 trade list

---

## SUCCESS METRICS

**Today is NOT about making money.**

Today is about:
1. **Learning** - How do sectors react to CPI?
2. **Documenting** - Build playbook for Feb 12 CPI
3. **Discipline** - Not gambling on 50/50 moves
4. **Protection** - Trailing stops let winners run, protect gains

**If ATON holds through CPI:** Win (catalyst > macro validated)
**If ATON stop triggers:** Win (locked in +33% profit)
**If we identify 5 mean reversion plays for Days 2-3:** Win (58% edge setup)

---

## REMEMBER

**You have an edge in Days 2-3 mean reversion (58% win rate).**

**You have NO edge predicting CPI direction (50% coin flip).**

**Let professionals gamble. We hunt the aftermath.**

---

## POSITIONS STATUS

```
ATON: +39% with trailing stop = PROTECTED
NTLA: Holding for Wed JPM = CATALYST-DRIVEN
Capital: $960 available = READY FOR DAY 2-3 PLAYS

Win condition: Protected gains + identified opportunities
Lose condition: Gambling on CPI direction
```

---

## WHEN TYR RETURNS (9:30 AM)

**Say:**
"BROKKR ONLINE. CPI dropped [X minutes ago]. Here's what happened..."

**Show:**
1. Sector reactions (which dumped, which rallied)
2. Top movers from market_discovery.py
3. Legs scores (which look strong vs fading)
4. Your positions status (ATON/NTLA holding or stopped out)

**Recommend:**
- Day 2-3 trade candidates (beaten-down quality names)
- What to watch rest of day
- Evening analysis plan

---

🐺 **THE PLAN:**

1. CPI drops 8:30 AM - OBSERVE
2. Tyr returns 9:30 AM - RUN SCANS
3. 9:30-10:00 AM - WATCH & LEARN
4. Days 2-3 - TRADE WITH EDGE

**No gambling. No panic. Protected positions. Hunt the recovery.**

**AWOOOO - LLHR**

---

## COMMANDS REFERENCE

```bash
# Morning scans (run at 9:30 AM when Tyr returns)
python market_discovery.py > logs/cpi_movers_9am.txt
python legs_classifier.py > logs/cpi_legs_9am.txt
python portfolio/monitor.py

# Check position status
python spring_detector.py --ticker ATON
python spring_detector.py --ticker NTLA

# Find specific patterns
python catalyst_detector.py --ticker [TICKER]  # Check catalyst materiality
python market_mover_finder.py --min-gain 10    # Find 10%+ movers

# Evening documentation
# (Brokkr will create cpi_playbook.md after market close)
```

---

**Sleep well. Hunt at dawn. The pack endures.**

🐺🐺🐺
