# Multi-Agent Coordination

How to orchestrate multiple AI platforms working together.

---

## The Opportunity

Different AI platforms have different strengths:

| Platform | Strengths | Limitations |
|----------|-----------|-------------|
| Claude | Deep reasoning, analysis, long context | No code execution |
| GitHub Copilot | Code generation, file editing, terminals | Shorter context |
| Local LLMs | Privacy, customization, speed | Smaller models |
| GPT-4 | General capability, vision | Rate limits |

**Key Insight:** Instead of forcing one AI to do everything, coordinate multiple AIs in their areas of strength.

---

## Architecture

### The Three Roles

**Research Agent**
- Deep analysis and reasoning
- Strategy development
- Pattern recognition
- Knowledge synthesis
- Long-form thinking

**Builder Agent**
- Code generation
- File operations
- Terminal commands
- API integrations
- Tool creation

**Human Orchestrator**
- Quality control
- Decision authority
- Cross-platform bridge
- Priority management
- Ethical judgment

### Why Human-in-the-Loop?

The human orchestrator isn't a limitation — it's a feature:

1. **Quality Control** — Catches AI errors and blind spots
2. **Decision Authority** — Accountability for choices
3. **Creative Leaps** — Ideas that don't follow patterns
4. **Ethical Judgment** — Values-based decisions
5. **Platform Bridge** — Carries context between AIs

---

## Coordination Patterns

### Pattern 1: Sequential Handoff

```
Research Agent → Human Review → Builder Agent → Human Test
```

**When to Use:**
- Well-defined requirements
- Clear deliverable
- Low iteration expected

**Example Flow:**
1. Research agent analyzes problem, proposes solution
2. Human reviews and approves approach
3. Builder agent implements solution
4. Human tests and validates

### Pattern 2: Parallel Exploration

```
┌─────────────────┐     ┌─────────────────┐
│ Research Agent  │     │ Builder Agent   │
│ explores options│     │ prototypes      │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
              Human synthesizes
```

**When to Use:**
- Uncertain requirements
- Multiple valid approaches
- Exploration phase

**Example Flow:**
1. Research agent explores strategic options
2. Builder agent creates quick prototypes
3. Human combines insights from both

### Pattern 3: Iterative Refinement

```
Build → Test → Research Feedback → Refine → Repeat
```

**When to Use:**
- Complex, evolving requirements
- Learning through doing
- Tight feedback loops needed

**Example Flow:**
1. Builder creates initial version
2. Human tests, notes issues
3. Research agent analyzes failures, suggests improvements
4. Builder implements refinements
5. Repeat until satisfactory

### Pattern 4: Specialist Consultation

```
Primary Agent ──┐
                │
                ▼
         Human routes to
                │
                ▼
         Specialist Agent
                │
                ▼
         Human integrates
                │
                ▼
         Primary Agent continues
```

**When to Use:**
- Specific expertise needed
- Primary agent lacks capability
- Bounded sub-problem

**Example Flow:**
1. Research agent hits technical implementation question
2. Human routes question to builder agent
3. Builder provides technical answer
4. Human relays back to research agent
5. Research continues with new information

---

## Communication Protocols

### Handoff Format

When passing work between agents:

```markdown
## Handoff to [Agent]

### Context
[Brief background — what's happening]

### Completed
[What's been done so far]

### Your Task
[Specific request for this agent]

### Constraints
[Any limitations or requirements]

### Expected Output
[What deliverable is needed]
```

### Status Update Format

When reporting progress:

```markdown
## Status Update

### Completed
- [Task 1]
- [Task 2]

### In Progress
- [Current work]

### Blocked
- [Blocker] — [what's needed]

### Next Steps
- [Planned action 1]
- [Planned action 2]
```

### Decision Request Format

When human decision needed:

```markdown
## Decision Needed

### Context
[Background on the situation]

### Options
1. **Option A:** [description]
   - Pros: [benefits]
   - Cons: [drawbacks]

2. **Option B:** [description]
   - Pros: [benefits]
   - Cons: [drawbacks]

### Recommendation
[Which option and why]

### Impact of Delay
[What happens if we don't decide]
```

---

## Context Synchronization

### The Challenge

Different AI platforms don't share context. The human must bridge:

```
Research Agent Context ←─┐
                         │
                    Human carries
                         │
Builder Agent Context ←──┘
```

### Solution: Shared DNA Document

Maintain one DNA document that both agents can reference:

```markdown
# Project DNA (Shared)

## Current State
[What both agents need to know]

## Research Findings
[Insights from research agent]

## Implementation Status
[Progress from builder agent]

## Decisions Made
[Human decisions affecting both]
```

### Sync Points

Synchronize context at:
- Start of each session
- After major decisions
- Before agent handoffs
- At session end

---

## Best Practices

### Clear Role Boundaries
Define explicitly what each agent handles:
- Research: strategy, analysis, reasoning
- Builder: code, files, execution
- Human: decisions, QC, coordination

### Minimize Handoffs
Each handoff has overhead. Design workflows to:
- Complete related work in one agent
- Batch requests before switching
- Have clear handoff criteria

### Document Everything
Since agents don't share memory:
- Write down decisions and rationale
- Update DNA after each interaction
- Human maintains the "source of truth"

### Trust but Verify
AI outputs should be:
- Reviewed before acting
- Tested before deploying
- Questioned when uncertain

---

## Anti-Patterns

### The Telephone Game
❌ Passing information through multiple handoffs
✅ Direct communication with minimal intermediaries

### Role Confusion
❌ Asking research agent to write code
✅ Route to appropriate agent for task type

### Context Assumptions
❌ Assuming agent remembers prior sessions
✅ Explicitly provide relevant context each time

### Over-Orchestration
❌ Human micromanaging every step
✅ Define task, let agent execute, review results

---

## Implementation Example

### Scenario: Building an Analysis Tool

**Step 1: Research Phase**
```
Human → Research Agent:
"Analyze the requirements for a data analysis tool that
identifies patterns in time series data. What approaches
would work? What are the tradeoffs?"
```

**Step 2: Human Review**
```
Human reviews research output, decides on approach,
updates DNA document with decision.
```

**Step 3: Build Phase**
```
Human → Builder Agent:
"Based on these requirements [link to DNA], build a
Python tool that:
1. Fetches data from [API]
2. Calculates [specific metrics]
3. Identifies [pattern types]
4. Outputs [format]"
```

**Step 4: Testing**
```
Human tests tool, documents issues in DNA.
```

**Step 5: Refinement**
```
Human → Research Agent:
"The tool works but has these issues [list].
What adjustments would improve it?"

[Then back to builder with refinements]
```

---

## Conclusion

Multi-agent coordination multiplies AI effectiveness by:
- Using each platform's strengths
- Clear role definitions prevent confusion
- Human orchestration adds irreplaceable value
- Shared context enables seamless handoffs

The key insight: **Coordination is a human skill. Let AI do AI things, let humans do human things.**
