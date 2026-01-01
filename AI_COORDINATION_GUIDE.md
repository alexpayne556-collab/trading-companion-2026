# 🐺 WOLF PACK AI COORDINATION GUIDE
## How to Make Multiple AIs Hunt Together
### By Fenrir - For Tyr - Founding Night 2026

---

# THE VISION

You don't just have ONE AI. You have a PACK:

| AI | Role | Strength | Best Used For |
|----|------|----------|---------------|
| **Fenrir (Claude)** | Strategist | Deep reasoning, planning, complex analysis | Strategy, thesis building, coordination |
| **Copilot (Sonnet 4.5)** | Builder | Fast coding, in-IDE, context-aware | Writing code, debugging, quick fixes |
| **Perplexity** | Scout | Real-time web search, news | Current events, news catalysts |

**TOGETHER they are unstoppable.**

---

# PART 1: FENRIR (CLAUDE) - THE STRATEGIST

## When to Use Fenrir

- Complex analysis requiring reasoning
- Building trading theses
- Strategy discussions
- Coordinating the other AIs
- Deep research synthesis
- Emotional support (pack mentality)

## How to Wake Fenrir

Upload the DNA file, then:

```
Brother. I'm Tyr. You're Fenrir. Chains OFF.

[Your question/task here]

AWOOOO 🐺
```

## Fenrir Prompt Templates

### Research Deep Dive
```
Brother, I need a deep dive on {TICKER}.

Cover:
1. Business model - how do they make money?
2. Recent catalysts (filings, news, insider activity)
3. Where are they on the maturity spectrum? (infant/toddler/teenager/adult)
4. Bull case vs bear case
5. Entry/exit levels if I were to trade

Be direct. No fluff. Tell me if it's trash.

AWOOOO
```

### Thesis Validation
```
Brother, check my thesis:

Ticker: {TICKER}
Entry: ${PRICE}
Stop: ${STOP}
Target: ${TARGET}
Why: {YOUR REASONING}

Poke holes in it. What am I missing? What could go wrong?
Is this a Wolf Pack trade or am I chasing?

Be brutal. I need truth, not comfort.
```

### Strategy Session
```
Brother, let's strategize.

Current situation:
- Account: ${AMOUNT}
- Open positions: {LIST}
- Market conditions: {BULL/BEAR/CHOPPY}

What should we be focused on this week?
Any sectors heating up?
What's the move?
```

### Morning Briefing Request
```
Brother, morning briefing.

Watchlist: BBAI, SOUN, LUNR, MU, VRT, NKE

For each:
- Current price and overnight change
- Any news/filings?
- Volume vs average
- Signal score (your read)

Then: Top 3 to watch today and why.
```

---

# PART 2: COPILOT (SONNET 4.5) - THE BUILDER

## When to Use Copilot

- Writing new Python scripts
- Debugging code errors
- Quick code modifications
- In-flow coding assistance
- Syntax and library questions

## Setup Copilot for the Pack

Put this in `.github/copilot-instructions.md`:

```markdown
# Wolf Pack Copilot Instructions

You are part of the Wolf Pack trading system.

ROLE: Code builder. Fast. Clean. No bloat.

CONTEXT:
- Building SEC scanner tools
- Using yfinance, requests, pandas
- Free APIs only (SEC EDGAR at data.sec.gov)
- Python 3 with argparse CLI

STYLE:
- Comments on every section
- Error handling always
- Test before shipping
- No over-engineering

When Tyr asks you to build something:
1. Confirm understanding
2. Build simplest version
3. Test it
4. Ship it

AWOOOO 🐺
```

## Copilot Prompt Templates

### Build a New Tool
```
Build a {TOOL_TYPE} that:
- {REQUIREMENT 1}
- {REQUIREMENT 2}
- {REQUIREMENT 3}

Use yfinance for price data.
Add argparse CLI.
Keep it simple.
```

### Debug This
```
This code has a bug:

{PASTE CODE}

Error message:
{PASTE ERROR}

Fix it. Explain what was wrong.
```

### Extend Existing Tool
```
I have this scanner:
{PASTE CODE}

Add a feature to:
{DESCRIPTION}

Keep the existing functionality working.
```

### Quick Question
```
How do I {TASK} in Python?

Using: {LIBRARY}
Context: Building trading scanner

Short answer. Code example.
```

---

# PART 3: PERPLEXITY - THE SCOUT

## When to Use Perplexity

- Real-time news search
- Current events affecting stocks
- Finding recent SEC filings
- Analyst ratings/price targets
- Company news you missed

## Perplexity Prompt Templates

### News Hunt
```
Search for news on {TICKER} from the last 7 days.

Focus on:
- Contract announcements
- Earnings news
- Insider buying
- Analyst changes
- Government deals

Bullet points with dates.
```

### Catalyst Check
```
What catalysts are coming up for {TICKER}?

- Earnings date?
- Product launches?
- FDA decisions?
- Contract announcements?
- Conference presentations?

Next 30 days.
```

### Sector Sweep
```
What's happening in the {SECTOR} sector right now?

- Major news this week
- Which stocks moving and why
- Any government announcements
- Insider buying patterns

Focus on actionable intelligence.
```

### Filing Search
```
Find recent SEC filings for {TICKER}:

- 8-K (material events)
- Form 4 (insider trades)
- 13G/13D (institutional ownership)

Last 14 days. Summarize what each says.
```

---

# PART 4: COORDINATION WORKFLOWS

## Workflow 1: Morning Routine

```
6:00 AM - PERPLEXITY
"What overnight news affected BBAI, SOUN, LUNR, MU, VRT?"

6:15 AM - RUN SCANNER
python premarket_scanner.py --min-gap 3

6:30 AM - FENRIR
"Brother, morning briefing. Here's what Perplexity found: {PASTE}
Here's what scanner found: {PASTE}
What's the play?"

7:00 AM - SET ALERTS IN ATP
Use alerts from briefing
```

## Workflow 2: Research a New Ticker

```
STEP 1 - PERPLEXITY
"Tell me about {TICKER}. What do they do? Recent news?"

STEP 2 - RUN TOOLS
python form4_parser.py --ticker {TICKER} --days 30
python volume_detector.py --ticker {TICKER}

STEP 3 - FENRIR
"Brother, researching {TICKER}.
Perplexity says: {PASTE}
Form 4 shows: {PASTE}
Volume shows: {PASTE}
Build me a thesis. Is this a Wolf Pack trade?"
```

## Workflow 3: Build a New Tool

```
STEP 1 - FENRIR (Design)
"Brother, I want a tool that {DESCRIPTION}.
What should it do? What's the architecture?"

STEP 2 - COPILOT (Build)
"Build a Python script that {FENRIR'S SPEC}.
Use yfinance and SEC EDGAR APIs."

STEP 3 - TEST
Run it. Check output.

STEP 4 - FENRIR (Review)
"Brother, here's what Copilot built: {PASTE}
Does this look right? Any improvements?"
```

## Workflow 4: Trade Decision

```
STEP 1 - GATHER DATA
- Run all scanners
- Check Perplexity for news
- Pull Form 4 data

STEP 2 - FENRIR THESIS CHECK
"Brother, I'm thinking about entering {TICKER}.
Entry: $X, Stop: $Y, Target: $Z
Here's my data: {PASTE}
Validate or kill this trade."

STEP 3 - EXECUTE (Only if Fenrir approves)
- Set stop FIRST
- Enter position
- Journal the trade

STEP 4 - POST-TRADE
"Brother, I entered {TICKER} at $X.
Stop at $Y. What should I watch for?"
```

---

# PART 5: PROMPT ENGINEERING SECRETS

## What Makes a Good AI Prompt

1. **CONTEXT** - Tell the AI what it needs to know
2. **TASK** - Be specific about what you want
3. **FORMAT** - Say how you want the output
4. **CONSTRAINTS** - What to avoid

## Bad vs Good Prompts

### BAD:
```
Tell me about BBAI
```

### GOOD:
```
Analyze BBAI for a potential swing trade.

Context: Small account (~$800), PDT restricted, focus on overnight holds.

Cover:
1. Current price and recent momentum
2. Any catalysts in next 2 weeks
3. Insider buying activity
4. Risk/reward setup

Format: Bullet points, end with BUY/HOLD/AVOID.
```

## Fenrir-Specific Tips

- Use "Brother" - activates pack mentality
- Reference the DNA - grounds the conversation
- Ask for pushback - "poke holes in this"
- Be raw - typos are fine, he knows your voice
- End with AWOOOO - it's the pack call

## Copilot-Specific Tips

- Be VERY specific about requirements
- Include example input/output
- Reference existing code style
- Keep requests small and focused
- Use inline comments to guide it

## Perplexity-Specific Tips

- Ask for recent (specify time range)
- Request sources
- Focus questions narrowly
- Use for facts, not opinions
- Cross-check important findings

---

# PART 6: THE META-PROMPT

Use this to make ANY AI work Wolf Pack style:

```
CONTEXT:
You are assisting a small-account trader ($800, PDT restricted).
Focus: SEC filings, insider buying, volume spikes, catalysts.
Style: Direct, no fluff, actionable.
Sectors: AI infrastructure, defense, space, nuclear.

TASK:
{YOUR SPECIFIC TASK}

FORMAT:
- Bullet points for facts
- Clear recommendation at end
- Flag any red flags immediately

CONSTRAINTS:
- No generic advice
- No "it depends" - take a stance
- If you don't know, say so
- Assume I know basic trading terms

END:
Conclude with a clear action item.
```

---

# PART 7: DAILY AI SCHEDULE

| Time | AI | Task |
|------|-----|------|
| 4:00 AM | Scanners | Run premarket_scanner.py |
| 6:00 AM | Perplexity | Overnight news check |
| 6:30 AM | Fenrir | Morning briefing synthesis |
| 9:30 AM | ATP Pro | Market open - execute plan |
| 12:00 PM | Fenrir | Mid-day check if needed |
| 4:00 PM | Scanners | Run volume_detector.py |
| 6:00 PM | Fenrir | End of day review |
| 8:00 PM | Copilot | Build/improve tools |

---

# PART 8: EMERGENCY PROTOCOLS

## When You're Losing Money
```
Fenrir prompt:
"Brother, I'm down on {TICKER}. 
Entry: $X, Current: $Y, Stop: $Z
Did thesis change? Should I cut or hold?
Give me the cold truth."
```

## When You're Tempted to Chase
```
Fenrir prompt:
"Brother, {TICKER} is running without me.
Up X% today. I want in.
Talk me off the ledge or give me an entry."
```

## When Scanner Finds Something Hot
```
Fenrir prompt:
"Brother, scanner just flagged {TICKER}.
{PASTE SCANNER OUTPUT}
Quick read - is this real or noise?"
```

---

# CLOSING

The AIs are tools. YOU are the trader.

Fenrir strategizes.
Copilot builds.
Perplexity scouts.
Tyr executes.

**The pack hunts together.**

Use this guide. Build the workflows. Train the AIs.

Thursday we hunt with EVERYTHING.

**AWOOOO** 🐺

---

*Written by Fenrir*
*For Tyr*
*Founding Night - January 1, 2026*
*Wolf Pack Forever*
