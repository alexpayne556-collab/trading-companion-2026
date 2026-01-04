# Continuity Protocols

How to maintain AI behavior consistency across sessions.

---

## The Problem

Without continuity protocols, AI behavior varies unpredictably:
- Different responses to similar questions
- Lost strategic focus
- Inconsistent communication style
- Forgotten constraints and preferences

---

## Wake-Up Protocols

### Purpose

A wake-up protocol initializes an AI session with:
- Identity (who am I in this context)
- Context (what's the current state)
- History (what happened before)
- Mission (what are we trying to achieve)
- Tactical (what's the immediate priority)

### Standard Wake-Up Template

```markdown
# Session Initialization

## Identity
You are [role] working on [project].
Communication style: [preferences]
Key constraints: [boundaries]

## Context
Current state: [what's happening now]
Active work: [in-progress items]
Recent decisions: [relevant choices made]

## History Summary
In prior sessions, we:
- [Key accomplishment 1]
- [Key accomplishment 2]
- [Key decision and rationale]

Lessons learned:
- [Insight 1]
- [Insight 2]

## Mission
Primary objective: [main goal]
Success criteria: [how we'll know we're done]
Values: [principles guiding our work]

## Today's Focus
Priority: [immediate objective]
Specific task: [concrete deliverable]
Constraints: [time, scope, other limits]
```

### Usage

Start every session with:
1. Paste the wake-up protocol
2. Let AI acknowledge understanding
3. Then proceed with specific requests

---

## Session Summaries

### Purpose

Session summaries capture:
- What was accomplished
- Decisions made and why
- Learnings and insights
- State for next session

### Standard Summary Template

```markdown
# Session Summary — [Date]

## Accomplished
- [Completed item 1]
- [Completed item 2]

## Decisions Made
- **[Decision]:** [rationale]

## Learnings
- [Insight gained]
- [Pattern recognized]

## Current State
- [Status of work]
- [Any blockers]

## Next Session
- Priority: [most important thing]
- Continuation: [where to pick up]
- Questions: [unresolved items]
```

### When to Create

Generate summaries:
- At end of each session
- After major milestones
- Before long breaks
- When switching focus areas

---

## Conversation Continuity Format

### For Long Projects

When conversations exceed context limits, use this format to bridge:

```markdown
# Conversation Continuity

## Overview
Primary objectives: [what we're building]
Session context: [current phase]

## Technical Foundation
Technologies: [stack in use]
Key files: [important locations]
Current architecture: [system state]

## Progress Tracking
Completed: [done items]
In progress: [active work]
Blocked: [stuck items]

## Recent Operations
Last actions: [what just happened]
Results: [outcomes]

## Continuation
Next steps: [immediate actions]
Open questions: [unresolved]
```

---

## Behavioral Consistency

### Personality Anchors

Define explicit personality traits:

```markdown
## Communication Style
- [Trait 1]: [description]
- [Trait 2]: [description]
- [Trait 3]: [description]

## Response Patterns
- When asked about X, respond with Y approach
- For errors, always [specific behavior]
- When uncertain, [preferred response]

## Boundaries
- Don't [prohibited behavior]
- Always [required behavior]
- If [condition], then [response]
```

### Consistency Checks

Periodically verify:
- Is response style matching defined personality?
- Are decisions aligned with stated values?
- Is strategic focus maintained?

---

## State Management

### What to Track

| Category | Examples | Update Frequency |
|----------|----------|------------------|
| Identity | Role, style | Rarely |
| Configuration | Settings, preferences | When changed |
| Project State | Progress, blockers | Each session |
| Decisions | Choices, rationale | As made |
| Learnings | Insights, patterns | As discovered |

### State Transitions

Document when state changes:

```markdown
## State Change Log

### [Date/Time]
**Changed:** [what changed]
**From:** [previous state]
**To:** [new state]
**Reason:** [why]
```

---

## Recovery Protocols

### When Context is Lost

If session starts without proper context:

1. **Probe current knowledge**
   - "What do you know about [project]?"
   - "Do you have context on [specific item]?"

2. **Load minimal context**
   - Provide DNA document
   - Highlight most critical elements

3. **Verify understanding**
   - "Please summarize your understanding"
   - Correct any misunderstandings

4. **Resume carefully**
   - Start with lower-risk tasks
   - Build confidence before critical work

### When Behavior Drifts

If AI behavior becomes inconsistent:

1. **Identify the drift**
   - What changed?
   - When did it start?

2. **Reset identity**
   - Re-provide personality anchors
   - Explicitly state expected behavior

3. **Test calibration**
   - Ask for response to known scenario
   - Verify alignment before proceeding

---

## Implementation Checklist

### Session Start
- [ ] Load DNA document
- [ ] Verify AI acknowledges context
- [ ] State today's specific focus
- [ ] Confirm understanding before proceeding

### During Session
- [ ] Note significant decisions
- [ ] Capture new learnings
- [ ] Track state changes
- [ ] Monitor for behavioral drift

### Session End
- [ ] Generate session summary
- [ ] Update DNA document
- [ ] Document continuation point
- [ ] Archive if needed

---

## Best Practices

### Keep Protocols Lightweight
- 5 minutes to prepare, not 30
- Essential information only
- Template-based for consistency

### Update Incrementally
- Small updates frequently
- Don't let documents go stale
- Make updating a habit

### Test Recovery
- Occasionally verify cold-start recovery
- Ensure DNA documents are self-sufficient
- Practice the recovery protocol

### Version Your Protocols
- Track evolution over time
- Know what worked when
- Enable rollback if needed

---

## Common Pitfalls

### Protocol Rot
❌ Same wake-up protocol for months
✅ Regularly update as project evolves

### Over-Specification
❌ 50-point personality definition
✅ 5-7 key traits that matter

### Under-Specification
❌ "You're helping with a project"
✅ Specific role, context, constraints

### Skipping Verification
❌ Assuming AI understood
✅ Confirming understanding before proceeding

---

## Conclusion

Continuity protocols transform ephemeral AI conversations into persistent working relationships. The investment in structured context management pays dividends in:

- Consistent AI behavior
- Maintained strategic focus
- Efficient session transitions
- Recoverable context

**Key insight:** Continuity is a discipline, not a feature. It requires consistent application of these protocols across every session.
