# LAYOUT 4: THE TRIGGER
## Executing the Trade with Precision

---

## PURPOSE OF THIS LAYOUT

Layout 4 is where you **PULL THE TRIGGER.**

You have a plan from L3. Now you:
1. Confirm the setup is still valid
2. Watch the order flow (Level 2)
3. Watch actual trades happening (Time & Sales)
4. Execute at the right moment
5. Immediately set your stop loss

**This layout is for ACTION, not analysis. You already did analysis.**

---

## WHAT YOU'LL BUILD

```
┌─────────────────────────────────────────────────────────────────┐
│                     LAYOUT 4: THE TRIGGER                       │
├─────────────────────────────┬───────────────────────────────────┤
│                             │                                   │
│   LEVEL 2 (ORDER BOOK)      │   1-MINUTE CHART                  │
│                             │                                   │
│   Shows:                    │   Shows:                          │
│   • All buy orders waiting  │   • Very short-term price action  │
│   • All sell orders waiting │   • Precise entry timing          │
│   • The spread              │                                   │
│   • Where support/resist is │   Indicators:                     │
│                             │   • VWAP (only)                   │
│   35% width                 │   • 9 EMA (only)                  │
│                             │   • Volume                        │
│   Symbol Group: ORANGE      │                                   │
│                             │   Symbol Group: ORANGE            │
│                             │   40% width                       │
├─────────────────────────────┼───────────────────────────────────┤
│                             │                                   │
│   TIME & SALES (TAPE)       │   ORDER ENTRY PANEL               │
│                             │                                   │
│   Shows:                    │   Where you:                      │
│   • Every trade that        │   • Enter your order              │
│     executes                │   • Set share quantity            │
│   • Green = bought at ask   │   • Set limit price               │
│   • Red = sold at bid       │   • Submit the trade              │
│   • Size of each trade      │                                   │
│                             │   25% width                       │
│   25% width                 │                                   │
│   Symbol Group: ORANGE      │                                   │
│                             │                                   │
└─────────────────────────────┴───────────────────────────────────┘
```

---

## STEP-BY-STEP BUILD INSTRUCTIONS

### STEP 1: Add Level 2

1. **Tools** → **Level 2** (might be called "Depth" or "Order Book")
2. Position on LEFT side (about 35% width)
3. Set Symbol Group to **ORANGE**

**Understanding Level 2:**

```
        BID SIDE                    ASK SIDE
   (Buyers waiting)             (Sellers waiting)
   
   Price    Size               Price    Size
   $3.74    500                $3.76    200
   $3.73    1,200              $3.77    800
   $3.72    800                $3.78    1,500
   $3.71    2,000              $3.79    400
   $3.70    5,000 ← Support    $3.80    3,000 ← Resistance
```

The SPREAD is the gap between highest bid and lowest ask.
In this example: $3.76 - $3.74 = $0.02 spread (tight, good)

### STEP 2: Add Time & Sales

1. **Tools** → **Time & Sales**
2. Position on BOTTOM LEFT (about 25% width)
3. Set Symbol Group to **ORANGE**

**Understanding Time & Sales:**

```
Time      Price    Size    
10:01:32  $3.76    500     ← GREEN (bought at ask = demand)
10:01:30  $3.74    200     ← RED (sold at bid = supply)
10:01:28  $3.76    1,000   ← GREEN (large buyer!)
10:01:25  $3.75    100     ← GREEN
```

- GREEN prints = Buyers aggressive (paying the ask)
- RED prints = Sellers aggressive (hitting the bid)
- Mostly GREEN = Buying pressure = Good for long entry

### STEP 3: Add 1-Minute Chart

1. **Tools** → **Chart**
2. Position on RIGHT side, top (about 40% width)
3. Set timeframe to **1 MIN**
4. Add indicators:

| Indicator | Color | Purpose |
|-----------|-------|---------|
| VWAP | Purple/Dotted | Today's fair price |
| EMA 9 | Yellow | Very short momentum |
| Volume | Default | Confirm the move |

5. Set Symbol Group to **ORANGE**

**Keep this chart CLEAN.** You don't need analysis here - you did that in L3. This is just for timing.

### STEP 4: Add Order Entry Panel

1. **Tools** → **Trade** (or "Order Entry" or "Directed Trading")
2. Position on BOTTOM RIGHT (about 25% width)

**Order Entry Fields:**
- Symbol: Will auto-fill from symbol group
- Action: Buy or Sell
- Quantity: Number of shares (from L3 calculation)
- Order Type: LIMIT (always use limit for small caps)
- Limit Price: Your entry price
- Time in Force: DAY (order expires end of day)

### STEP 5: Save the Layout

1. Save as **"L4 - Trigger"**

---

## HOW TO USE LAYOUT 4

### THE EXECUTION SEQUENCE (2 minutes)

**STEP 1: TYPE YOUR TICKER**
- Enter the symbol
- All tools update (Level 2, T&S, Chart, Order Entry)

**STEP 2: PRE-FILL YOUR ORDER (Don't Submit Yet)**
- Quantity: From your L3 position size calculation
- Order Type: LIMIT
- Limit Price: Your planned entry price
- Time in Force: DAY

**STEP 3: RUN THE EXECUTION CHECKLIST**

```
30-SECOND EXECUTION CHECKLIST
═══════════════════════════════════════════════════

LEVEL 2 CHECK:
□ Is the spread reasonable? (<$0.05 for stocks under $20)
□ Are bids stacking at or near my entry price?
□ Is there a large sell wall I need to worry about?

TIME & SALES CHECK:
□ Am I seeing more GREEN prints than RED?
□ Are there any large prints (1,000+ shares)?
□ Is the tape ACTIVE (trades happening) or DEAD?

1-MINUTE CHART CHECK:
□ Is price above VWAP? (or reclaiming it)
□ Is the current candle green or at least holding?
□ Is volume present on this move?

SCORING:
6+ checks = EXECUTE NOW
4-5 checks = EXECUTE with caution
3 or fewer = WAIT or ABORT
═══════════════════════════════════════════════════
```

**STEP 4: EXECUTE**

If checklist passes:
1. Verify order details one more time
2. Click BUY / SUBMIT
3. Watch for fill confirmation

**STEP 5: IMMEDIATELY SET STOP LOSS**

This is CRITICAL. The moment you get filled:
1. Change order Action to SELL
2. Order Type: STOP (or STOP LIMIT)
3. Stop Price: Your stop price from L3
4. Quantity: Same as your position
5. Time in Force: GTC (Good Til Cancelled) or DAY
6. SUBMIT

**Your stop should be live within 30 seconds of your entry.**

**STEP 6: MOVE TO L5**

Once entry is filled and stop is set:
→ Move to Layout 5 to manage the position

---

## READING LEVEL 2 LIKE A PRO

### BULLISH LEVEL 2 SIGNS:
- Bids are LARGER than asks (more buyers waiting)
- Bids are STACKING at higher prices (support building)
- Asks are THINNING out (less resistance)
- Spread is TIGHTENING (supply/demand balancing)

### BEARISH LEVEL 2 SIGNS:
- Asks are LARGER than bids (sellers in control)
- Large sell wall at a specific price (resistance)
- Bids are DISAPPEARING (support failing)
- Spread is WIDENING (uncertainty)

### IMPORTANT:
Level 2 can be manipulated. Large players can:
- Place fake orders to scare/attract others
- Pull orders before they get hit

**Use Level 2 as ONE input, not the only input.**

---

## READING TIME & SALES LIKE A PRO

### WHAT TO WATCH FOR:

**BUYING PRESSURE (Good for Longs):**
```
Time      Price    Size    Color
10:05:01  $3.80    2,000   GREEN  ← Large buyer at ask!
10:05:00  $3.80    500     GREEN
10:04:58  $3.80    800     GREEN
10:04:55  $3.79    200     GREEN
```
Multiple green prints, price ticking UP = buyers in control

**SELLING PRESSURE (Bad for Longs):**
```
Time      Price    Size    Color
10:05:01  $3.76    1,500   RED    ← Large seller at bid!
10:05:00  $3.77    400     RED
10:04:58  $3.77    600     RED
10:04:55  $3.78    200     RED
```
Multiple red prints, price ticking DOWN = sellers in control

**ABSORPTION (Bullish):**
```
Large sell orders hitting the bid...
But price NOT dropping...
Someone is ABSORBING the selling = hidden buyer
```

**EXHAUSTION (Reversal Warning):**
```
Price up on smaller and smaller prints
Volume fading
Spread widening
= Move may be ending
```

---

## ORDER TYPES EXPLAINED

### MARKET ORDER
- Executes immediately at best available price
- **DANGER:** On small caps, you might get a bad fill
- **USE:** Only in emergencies or very liquid stocks

### LIMIT ORDER (USE THIS)
- Executes at your price or better
- Won't fill if price moves away from you
- **USE:** Almost always for entries

### STOP ORDER (For Your Stop Loss)
- Becomes a market order when stop price is reached
- Protects you automatically
- **USE:** For stop losses

### STOP LIMIT ORDER
- Becomes a limit order when stop price is reached
- More control, but might not fill if price gaps
- **USE:** When you want more control on stop execution

---

## COMMON EXECUTION MISTAKES

### MISTAKE 1: Using Market Orders
- "I just want to get in!"
- On small caps, the spread can eat your profit
- A $0.10 bad fill on a $4 stock is 2.5% gone instantly
- **FIX:** Always use limit orders

### MISTAKE 2: Forgetting the Stop
- You get filled, excited, start watching profit
- Forget to set stop
- Stock reverses, you panic sell at the worst time
- **FIX:** Stop is set BEFORE you celebrate

### MISTAKE 3: Chasing
- Setup was at $3.75
- You hesitate
- Now it's at $3.90
- You market order in because "it's going up!"
- It reverses to $3.70
- **FIX:** If you miss the entry, let it go. Wait for pullback or next setup.

### MISTAKE 4: Fighting the Tape
- Level 2 shows heavy selling
- Time & Sales is all red
- But you "believe in the stock"
- You buy anyway
- **FIX:** If the tape says no, listen

### MISTAKE 5: Overcomplicating
- You spend 10 minutes in L4 analyzing
- By then, the opportunity is gone
- **FIX:** 2 minutes max. Check, execute, set stop, move to L5.

---

## THE PERFECT EXECUTION

**STEP 1:** Price approaches your entry zone from L3

**STEP 2:** You switch to L4

**STEP 3:** Quick checklist (30 seconds):
- Level 2: Bids holding ✓
- T&S: Green prints ✓
- Chart: Above VWAP ✓

**STEP 4:** Order pre-filled:
- 50 shares
- Limit $3.75
- Click BUY

**STEP 5:** Filled at $3.75

**STEP 6:** Immediately:
- Stop order
- Stop price $3.45
- 50 shares
- Click SELL

**STEP 7:** Switch to L5 to manage

**Total time in L4: Under 2 minutes**

---

## WHAT YOU DO NEXT

**If you got filled:**
→ Confirm stop is set
→ Move to L5 (Command)
→ Manage the position

**If you didn't get filled (price moved away):**
→ Cancel unfilled order
→ Go back to L3
→ Reassess: Wait for pullback? Adjust price? Move on?

**If checklist failed:**
→ Don't force it
→ Go back to L2/L3
→ Wait for better confirmation

---

## CHECKLIST BEFORE LEAVING L4

- [ ] Entry order is FILLED (not just submitted)
- [ ] Stop loss order is LIVE
- [ ] I noted my entry price
- [ ] I know my stop price
- [ ] I know my target price
- [ ] Position shows in my account

---

## SUMMARY

| What You Do | Why | Time |
|-------------|-----|------|
| Level 2 check | See if buyers/sellers support your thesis | 15 sec |
| Time & Sales check | Confirm actual buying pressure | 15 sec |
| Chart check | Confirm price action | 10 sec |
| Execute order | Enter the position | 10 sec |
| Set stop | Protect capital | 30 sec |

**Output from L4:** Live position with stop loss set

---

*Next: Layout 5 - Command Center*
