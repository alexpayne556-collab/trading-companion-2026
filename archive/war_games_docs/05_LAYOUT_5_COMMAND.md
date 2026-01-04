# LAYOUT 5: COMMAND CENTER
## Managing Positions to Maximize Profit and Minimize Loss

---

## PURPOSE OF THIS LAYOUT

Layout 5 is your **MISSION CONTROL** for open positions.

Once you're in a trade, your job is:
1. Monitor the position
2. Move stop to breakeven when appropriate
3. Take partial profits at targets
4. Exit when target is hit OR stop is hit
5. Never let a winner become a big loser

**This is where discipline makes or breaks you.**

---

## WHAT YOU'LL BUILD

```
┌─────────────────────────────────────────────────────────────────┐
│                   LAYOUT 5: COMMAND CENTER                      │
├─────────────────────────────┬───────────────────────────────────┤
│                             │                                   │
│   POSITIONS PANEL           │   15-MINUTE CHART                 │
│                             │                                   │
│   Shows all open positions: │   Your active position chart      │
│   • Symbol                  │                                   │
│   • Shares                  │   Draw on chart:                  │
│   • Avg Cost (your entry)   │   • Entry line (green)            │
│   • Current Price           │   • Stop line (red)               │
│   • $ P&L                   │   • Target line (blue)            │
│   • % P&L                   │                                   │
│                             │   Indicators:                     │
│   Click position →          │   9 EMA, 21 EMA, VWAP, Volume    │
│   chart updates             │                                   │
│                             │   Symbol Group: PURPLE            │
│   Symbol Group: PURPLE      │                                   │
│   30% width                 │   45% width                       │
│                             │                                   │
├─────────────────────────────┼───────────────────────────────────┤
│                             │                                   │
│   ORDERS PANEL              │   ALERTS PANEL                    │
│                             │                                   │
│   Shows pending orders:     │   Your price alerts:              │
│   • Stop losses             │   • Target approaching            │
│   • Limit sells             │   • Key levels                    │
│   • Can modify/cancel here  │   • New setups on watchlist       │
│                             │                                   │
│   15% width                 │   10% width                       │
│                             │                                   │
└─────────────────────────────┴───────────────────────────────────┘
```

---

## STEP-BY-STEP BUILD INSTRUCTIONS

### STEP 1: Add Positions Panel

1. **Tools** → **Positions**
2. Position on LEFT side (about 30% width)
3. Make sure these columns are visible:
   - Symbol
   - Quantity (shares)
   - Avg Cost (your entry price)
   - Last (current price)
   - Day Gain/Loss
   - Total Gain/Loss ($)
   - Total Gain/Loss (%)
4. Set Symbol Group to **PURPLE**

### STEP 2: Add Orders Panel

1. **Tools** → **Orders** (or "Open Orders")
2. Position on BOTTOM LEFT (about 15% width)
3. This shows your pending orders (stops, limits)

### STEP 3: Add 15-Minute Chart

1. **Tools** → **Chart**
2. Position on RIGHT side (about 45% width, full height)
3. Set timeframe to **15 MIN**
4. Add indicators:

| Indicator | Period | Color |
|-----------|--------|-------|
| EMA | 9 | Yellow |
| EMA | 21 | Blue |
| VWAP | Default | Purple |
| Volume | Default | Default |

5. Set Symbol Group to **PURPLE**
6. Enable Extended Hours

### STEP 4: Add Alerts Panel

1. **Tools** → **Alerts**
2. Position on BOTTOM RIGHT (about 10% width)
3. You'll set alerts for key price levels

### STEP 5: Save the Layout

1. Save as **"L5 - Command"**

---

## HOW TO USE LAYOUT 5

### WHEN YOU FIRST ARRIVE FROM L4

**Step 1: Verify Your Position**
- Click on your position in the Positions panel
- Chart updates to show that stock
- Verify: Entry price matches what you expected

**Step 2: Verify Your Stop is Active**
- Check Orders panel
- You should see your STOP order
- Verify: Stop price is correct

**Step 3: Draw Your Levels on the Chart**
- Use horizontal line tool
- GREEN line at your entry price
- RED line at your stop price
- BLUE line at your target price

Now you have a visual guide.

**Step 4: Set Alerts**
- Alert 1: Price at 50% to target (consider partial profit)
- Alert 2: Price at target (take profit)
- Alert 3: Price near stop (prepare for exit)

---

## POSITION MANAGEMENT RULES

### THE PROFIT MANAGEMENT LADDER

**Your position goes through stages. Here's what to do at each:**

```
STAGE 1: INITIAL POSITION
═══════════════════════════════════════════════════
Status: Just entered, stop is set
Risk: Full original risk
Action: WAIT. Let the trade work.
Do NOT: Move stop further away, add to position
═══════════════════════════════════════════════════

STAGE 2: TRADE MOVES IN YOUR FAVOR (+1R)
═══════════════════════════════════════════════════
Status: Profit equals your initial risk amount
Example: You risked $0.30/share, now up $0.30/share

Action: MOVE STOP TO BREAKEVEN
- Adjust stop order to your entry price
- You now have a "FREE TRADE"
- If it reverses, you lose nothing

Do NOT: Get greedy and remove stop entirely
═══════════════════════════════════════════════════

STAGE 3: APPROACHING FIRST TARGET (+1.5R to +2R)
═══════════════════════════════════════════════════
Status: Halfway to your target
Example: Target was +$0.60, you're at +$0.40

Action: TAKE PARTIAL PROFIT
- Sell 50% of your position
- Lock in real profit
- Let remaining 50% run

Adjust stop: Keep at breakeven or move up slightly
═══════════════════════════════════════════════════

STAGE 4: AT TARGET (+2R to +3R)
═══════════════════════════════════════════════════
Status: Price reaches your target

Action: TAKE MORE PROFIT
- Sell another 25-50% of position
- You've now locked in most profit

Remaining shares: Trail stop behind price
- Move stop up as price rises
- Give it room to run
═══════════════════════════════════════════════════

STAGE 5: EXTENDED MOVE (Beyond Target)
═══════════════════════════════════════════════════
Status: Stock keeps running past your target

Action: TRAIL YOUR STOP
- Move stop to below each new swing low
- Or use 9 EMA as trailing stop
- Let winner run but protect profit

Exit when: Stop gets hit OR end of day
═══════════════════════════════════════════════════
```

---

## THE MATH OF PARTIAL PROFITS

**Example Position:**
- Entry: $3.75
- Stop: $3.45 (Risk = $0.30/share)
- Target: $4.35 (Reward = $0.60/share)
- Shares: 100
- Total Risk: 100 × $0.30 = $30

**How Partial Profits Work:**

```
AT +1R ($4.05):
- Move stop to breakeven ($3.75)
- Risk is now $0

AT +1.5R ($4.20):
- Sell 50 shares at $4.20
- Profit locked: 50 × ($4.20 - $3.75) = $22.50
- Remaining: 50 shares with stop at $3.75

AT +2R ($4.35 - Target):
- Sell 25 more shares at $4.35
- Profit locked: 25 × ($4.35 - $3.75) = $15.00
- Total locked profit: $22.50 + $15.00 = $37.50
- Remaining: 25 shares with trailing stop

IF IT RUNS TO $4.80:
- Final 25 shares stopped out at $4.50 (trailing stop)
- Final profit: 25 × ($4.50 - $3.75) = $18.75
- TOTAL PROFIT: $37.50 + $18.75 = $56.25

IF IT REVERSES AFTER PARTIAL:
- Final 25 shares stopped at breakeven ($3.75)
- Final profit: $0 on those shares
- TOTAL PROFIT: $37.50 (still profitable!)
```

**The beauty:** You can't lose money after you take partials and move stop to breakeven.

---

## WHEN TO EXIT COMPLETELY

### EXIT 1: Stop Loss Hit
- Price hits your stop
- You're out automatically (stop order executes)
- **Accept it.** This is the cost of doing business.
- DO NOT re-enter the same trade immediately

### EXIT 2: Target Hit
- Price hits your profit target
- Take all remaining shares off
- **Celebrate.** You followed your plan.

### EXIT 3: Thesis Breaks
Even if stop isn't hit, exit if:
- News changes the story (bad earnings, lost contract)
- Sector suddenly reverses hard
- Stock action doesn't match the setup (heavy selling)

**Example:** You're long RCAT on defense strength. Pentagon announces major budget cuts. Even if your stop isn't hit yet, the THESIS is broken. Exit.

### EXIT 4: End of Day (For Day Trades)
If you're day trading (not holding overnight):
- Close all positions before 3:45 PM
- Don't hold small caps overnight unless planned

### EXIT 5: Time Stop
If trade goes nowhere for days:
- Capital is tied up
- Opportunity cost
- Consider exiting even at small loss/gain
- Find better opportunities

---

## THE CARDINAL RULES OF L5

### RULE 1: NEVER MOVE STOP FURTHER AWAY
- Your stop is where you're WRONG
- If you move it further, you're just hoping
- Hope is not a strategy
- **This rule saves accounts**

### RULE 2: NEVER REMOVE YOUR STOP
- "I'll watch it closely" = recipe for disaster
- One bathroom break + one news bomb = blown account
- Stops are automatic protection. Keep them.

### RULE 3: LET WINNERS RUN (With Protection)
- Don't take full profit at +10% if it can go +30%
- USE partial profits + trailing stops
- Capture the big moves, they make your year

### RULE 4: CUT LOSERS QUICKLY
- Stop hits? You're out. No questions.
- Don't add to losers ("averaging down")
- Small losses are fine. Big losses kill.

### RULE 5: DON'T OVERTRADE FROM L5
- You're here to MANAGE, not find new trades
- Manage your positions
- Check L1/L2 occasionally for new setups
- But don't abandon management for new shiny objects

---

## DAILY P&L MANAGEMENT

### TRACKING YOUR DAY

Keep track in L5:
- How many trades today?
- Win/loss count
- Total $ P&L for the day

### DAILY LOSS LIMIT

**HARD RULE:** If you lose 5% of your account in one day, STOP TRADING.

For $700 account: -$35 daily loss limit

**What to do:**
1. Close all positions
2. Close Fidelity
3. Walk away
4. Review what went wrong
5. Come back tomorrow

**Why:** After a bad day, emotions take over. You'll revenge trade, make it worse. Stopping saves you.

---

## END OF DAY ROUTINE

**3:30 PM - Decision Time:**

For each open position, decide:

**CLOSE IT?**
- Was this a day trade? Close it.
- Is there overnight risk (earnings, news)? Close it.
- Am I uncomfortable holding overnight? Close it.

**HOLD IT?**
- Was this a swing trade from the start? Hold it.
- Is the thesis intact and trend strong? Hold it.
- Is stop loss set (and wide enough for overnight)? Hold it.

**4:00 PM - Market Close:**
- Review the day
- Note what worked, what didn't
- Update watchlists for tomorrow
- Set any alerts for overnight

---

## CHECKLIST FOR L5

**When entering L5:**
- [ ] Position verified
- [ ] Stop loss is live
- [ ] Levels drawn on chart
- [ ] Alerts set

**During the trade:**
- [ ] Moved stop to breakeven at +1R
- [ ] Took partial at target 1
- [ ] Trailing stop on remainder

**End of trade:**
- [ ] Full exit at target OR stop
- [ ] Noted result (win/loss, amount)
- [ ] Reviewed: Did I follow my rules?

---

## SUMMARY

| Task | When | Action |
|------|------|--------|
| Verify position/stop | Immediately after L4 | Confirm everything is set |
| Draw levels on chart | First 2 minutes | Visual guide |
| Move stop to breakeven | At +1R profit | Eliminate risk |
| Take partial profit | At +1.5R to +2R | Lock in gains |
| Trail stop | Beyond target | Let winners run |
| Exit | At target, stop, or thesis break | Complete the trade |

**Output from L5:** Completed trades with disciplined management

---

## THE FINAL WORD

Most traders lose money not because they pick bad stocks, but because they:
1. Don't have stops
2. Move stops further away
3. Take profits too early
4. Let losers run too long

**L5 is where you become a professional.** Follow the rules. Manage the trade. Protect your capital.

---

*This completes the 5-Layout system. See 07_TICKER_THESIS.md for your sector analysis.*
