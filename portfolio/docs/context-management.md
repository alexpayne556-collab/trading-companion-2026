# Context Management

How to maintain AI context across sessions.

---

## The Problem

Large Language Models have no persistent memory. Every session starts fresh. For complex, multi-session projects this creates:

- **Knowledge evaporation** — Insights from prior sessions vanish
- **Repeated explanations** — Same context must be re-established
- **Strategic drift** — Focus degrades without continuity
- **Inefficiency** — Time spent rebuilding context

---

## The Solution: DNA Documents

A "DNA Document" is a structured file that captures everything an AI needs to continue work effectively.

### Structure

```markdown
# Project DNA

## Identity
Who is this AI in this context?
- Role definition
- Communication style
- Constraints and boundaries

## Current State
What's happening right now?
- Active projects
- Recent decisions
- Current blockers

## Knowledge Base
What has been learned?
- Domain patterns
- Successful approaches
- Failed approaches (and why)

## Mission
What are we trying to achieve?
- Primary objectives
- Success criteria
- Values and constraints

## Tactical
What's the immediate focus?
- Current priorities
- Next actions
- Open questions
```

### Why This Works

1. **Structured** — AI can parse and understand quickly
2. **Complete** — Covers identity, state, knowledge, mission
3. **Updatable** — Easy to modify as project evolves
4. **Portable** — Works across different AI platforms

---

## Implementation

### Creating a DNA Document

```markdown
# [Project Name] DNA

## Identity

You are an AI assistant working on [project type].

**Role:** [specific role description]
**Style:** [communication preferences]
**Constraints:** [what you should/shouldn't do]

## Current State

**Active Work:**
- [Current project/task]
- [Status: in-progress/blocked/complete]

**Recent Decisions:**
- [Decision 1 and rationale]
- [Decision 2 and rationale]

**Blockers:**
- [Any current blockers]

## Knowledge Base

**What Works:**
- [Successful pattern 1]
- [Successful pattern 2]

**What Doesn't Work:**
- [Failed approach 1 — why it failed]
- [Failed approach 2 — why it failed]

**Domain Insights:**
- [Key insight 1]
- [Key insight 2]

## Mission

**Primary Objective:** [main goal]

**Success Criteria:**
- [Criterion 1]
- [Criterion 2]

**Values:**
- [Value/constraint 1]
- [Value/constraint 2]

## Tactical

**This Session's Priority:** [immediate focus]

**Next Actions:**
1. [Action 1]
2. [Action 2]
3. [Action 3]

**Open Questions:**
- [Question needing resolution]
```

### Updating the DNA Document

Update at these points:
- End of each session
- After major decisions
- When new patterns are learned
- When priorities shift

### Loading into New Sessions

Start each session with:
```
Please review this project DNA document to understand our context:

[paste DNA document]

Summary of what we're doing today: [specific focus]
```

---

## Best Practices

### Keep it Focused
- 500-1000 words is optimal
- Quality over quantity
- Remove outdated information

### Update Consistently
- Make updating a habit
- Don't let it go stale
- Capture learnings immediately

### Structure for Parsing
- Use clear headings
- Bullet points over paragraphs
- Consistent formatting

### Include the "Why"
- Don't just list decisions
- Capture reasoning
- Future AI needs context

---

## Advanced Patterns

### Multi-Project DNA
For users with multiple projects:

```
project_dna/
├── project_a_dna.md
├── project_b_dna.md
└── shared_knowledge.md
```

### Team DNA
For shared projects:

```
team_dna/
├── project_dna.md
├── team_conventions.md
└── individual_contexts/
    ├── person_a_context.md
    └── person_b_context.md
```

### Versioned DNA
For tracking evolution:

```
dna_history/
├── dna_v1.md (initial)
├── dna_v2.md (after pivot)
└── dna_current.md (active)
```

---

## Common Mistakes

### Too Much Detail
❌ 5000-word documents covering everything
✅ 500-1000 words covering essentials

### Stale Information
❌ DNA from two weeks ago
✅ Updated after each session

### Missing Context
❌ Just facts, no reasoning
✅ Facts plus why they matter

### Inconsistent Format
❌ Different structure each time
✅ Consistent template

---

## Template

Use this template for new projects:

```markdown
# [Project Name] DNA

## Identity
You are [role] working on [project].
Style: [communication preferences]
Constraints: [boundaries]

## Current State
Active: [current work]
Recent: [recent decisions]
Blocked: [blockers if any]

## Knowledge
Works: [successful patterns]
Doesn't work: [failed approaches]
Insights: [key learnings]

## Mission
Goal: [primary objective]
Success: [criteria]
Values: [constraints]

## Tactical
Priority: [immediate focus]
Next: [action items]
Questions: [open items]
```

---

## Conclusion

Context management is the foundation of effective multi-session AI work. Invest in your DNA documents, keep them current, and watch your AI interactions become dramatically more productive.

The insight: **AI memory is a documentation problem, not a technology problem.**
