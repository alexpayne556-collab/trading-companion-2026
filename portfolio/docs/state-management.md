# State Management

How to track and persist AI state across sessions and platforms.

---

## Overview

State management ensures that:
- Progress is never lost
- Decisions are documented
- Context can be restored
- Multiple agents stay synchronized

---

## State Categories

### 1. Identity State (Static)

What the AI "is" in this context:
- Role definition
- Communication style
- Constraints and boundaries
- Domain expertise

**Update Frequency:** Rarely (only when role changes)

### 2. Project State (Dynamic)

Current status of work:
- Active tasks
- Completed items
- Blocked items
- Open questions

**Update Frequency:** Every session

### 3. Knowledge State (Cumulative)

What has been learned:
- Successful patterns
- Failed approaches
- Domain insights
- Edge cases discovered

**Update Frequency:** As learnings occur

### 4. Decision State (Event-Driven)

Choices made and rationale:
- What was decided
- What options were considered
- Why this option was chosen
- Expected outcomes

**Update Frequency:** As decisions are made

---

## State Storage

### Primary: DNA Document

The DNA document is the single source of truth:

```markdown
# [Project] DNA

## Identity State
Role: [definition]
Style: [preferences]
Constraints: [boundaries]

## Project State
Active: [current work]
Completed: [done items]
Blocked: [stuck items]

## Knowledge State
Works: [successful approaches]
Doesn't: [failed approaches]
Insights: [key learnings]

## Decision Log
### [Date] - [Decision Title]
- Choice: [what was decided]
- Options: [alternatives considered]
- Rationale: [why this choice]
```

### Secondary: Session Logs

Individual session records:

```
session_logs/
├── 2024-01-15_session.md
├── 2024-01-16_session.md
└── 2024-01-17_session.md
```

### Tertiary: Artifacts

Produced outputs:
- Code files
- Documentation
- Exports
- Reports

---

## State Transitions

### Tracking Changes

Document state changes explicitly:

```markdown
## State Change: [Date/Time]

### Category
[Identity | Project | Knowledge | Decision]

### Change
From: [previous state]
To: [new state]

### Reason
[Why the change occurred]

### Impact
[What this affects]
```

### State Lifecycle

```
┌─────────────┐
│   INITIAL   │ ← First session, no prior state
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   ACTIVE    │ ← State being modified
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  PERSISTED  │ ← State saved to DNA/logs
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  RESTORED   │ ← State loaded into new session
└─────────────┘
```

---

## Synchronization

### Single Agent, Multiple Sessions

```
Session 1 → Save State → DNA Document
                              │
                              ▼
DNA Document → Load State → Session 2
```

**Protocol:**
1. End each session with summary
2. Update DNA document
3. Start next session with wake-up protocol
4. Verify state loaded correctly

### Multiple Agents, Shared Project

```
Research Agent ─────┐
                    │
                    ▼
              DNA Document (Shared)
                    │
                    ▼
Builder Agent ──────┘
```

**Protocol:**
1. Each agent updates DNA after work
2. Human verifies no conflicts
3. Next agent loads fresh DNA
4. Human bridges any gaps

### Conflict Resolution

When agents have conflicting state:

1. **Detect conflict** — States don't match
2. **Identify source** — Which update caused divergence
3. **Resolve** — Human decides correct state
4. **Update** — Correct DNA document
5. **Propagate** — Ensure all agents have correct state

---

## State Queries

### Current State Check

Ask the AI:
```
What is your understanding of:
- Current project state
- Your role
- Recent decisions
- Immediate priorities
```

### State Validation

Verify state accuracy:
```
Please confirm:
- Active tasks: [list]
- Last completed: [item]
- Current blockers: [list]
- Next action: [item]

Is this accurate?
```

### State Diff

Compare states:
```
State at session start:
[state A]

State at session end:
[state B]

What changed?
```

---

## Persistence Patterns

### Append-Only Log

Never delete, only append:

```markdown
## Decision Log

### 2024-01-15 - Chose Python
[decision details]

### 2024-01-16 - Revised to use async
[decision details]

### 2024-01-17 - Added caching
[decision details]
```

**Benefit:** Complete history, can trace evolution

### Snapshot + Delta

Periodic full snapshots, frequent deltas:

```
snapshots/
├── 2024-01-01_full.md
└── 2024-01-15_full.md

deltas/
├── 2024-01-02_changes.md
├── 2024-01-03_changes.md
└── ...
```

**Benefit:** Fast recovery, efficient updates

### Rolling Window

Keep recent history, archive old:

```markdown
## Recent State (Last 5 Sessions)
[Detailed state]

## Archived State (Summary)
[Condensed historical state]
```

**Benefit:** Manageable document size

---

## Implementation

### State Manager Pseudocode

```python
class StateManager:
    def __init__(self, dna_path):
        self.dna_path = dna_path
        self.state = self.load()
    
    def load(self):
        """Load state from DNA document"""
        with open(self.dna_path) as f:
            return parse_dna(f.read())
    
    def save(self):
        """Persist current state to DNA"""
        content = generate_dna(self.state)
        with open(self.dna_path, 'w') as f:
            f.write(content)
    
    def update(self, category, key, value, reason):
        """Update state with change tracking"""
        old_value = self.state[category].get(key)
        self.state[category][key] = value
        self.log_change(category, key, old_value, value, reason)
    
    def log_change(self, category, key, old, new, reason):
        """Record state transition"""
        self.state['changelog'].append({
            'timestamp': now(),
            'category': category,
            'key': key,
            'from': old,
            'to': new,
            'reason': reason
        })
```

---

## Best Practices

### Single Source of Truth
- One DNA document per project
- All agents reference same document
- Human maintains integrity

### Explicit Over Implicit
- Document state changes explicitly
- Don't assume state persists
- Verify state after loading

### Atomic Updates
- Update related state together
- Don't leave partial updates
- Validate consistency

### Backup Critical State
- Version control DNA documents
- Regular backups
- Test recovery periodically

---

## Anti-Patterns

### State Sprawl
❌ State scattered across many files
✅ Consolidated in DNA document

### Silent Updates
❌ Changing state without documentation
✅ Explicit change records

### Stale State
❌ DNA document not updated
✅ Regular maintenance habit

### Assumption of Persistence
❌ "The AI remembers from last time"
✅ "I'll verify state before proceeding"

---

## Conclusion

Effective state management enables:
- Seamless session transitions
- Multi-agent coordination
- Complete audit trails
- Reliable recovery

The key insight: **State is your responsibility, not the AI's.** Design your state management, maintain it consistently, and verify it regularly.
