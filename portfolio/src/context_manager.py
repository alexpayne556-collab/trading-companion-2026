"""
Context Manager
===============
Core module for managing AI context across sessions.

This module provides utilities for:
- Loading context from DNA documents
- Updating state as work progresses
- Generating summaries for session continuity
- Exporting state for cross-platform coordination
"""

import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class IdentityState:
    """Static state: who the AI 'is' in this context"""
    role: str
    style: str
    constraints: List[str] = field(default_factory=list)
    domain_expertise: List[str] = field(default_factory=list)


@dataclass
class ProjectState:
    """Dynamic state: current work status"""
    active_tasks: List[str] = field(default_factory=list)
    completed_tasks: List[str] = field(default_factory=list)
    blocked_tasks: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)


@dataclass
class KnowledgeState:
    """Cumulative state: what has been learned"""
    successful_patterns: List[str] = field(default_factory=list)
    failed_approaches: List[str] = field(default_factory=list)
    domain_insights: List[str] = field(default_factory=list)


@dataclass
class Decision:
    """Record of a decision made"""
    timestamp: str
    title: str
    choice: str
    options_considered: List[str]
    rationale: str


@dataclass
class StateChange:
    """Record of a state transition"""
    timestamp: str
    category: str
    key: str
    from_value: Any
    to_value: Any
    reason: str


class ContextManager:
    """
    Manages AI context across sessions.
    
    Usage:
        # Initialize
        ctx = ContextManager("project_dna.json")
        
        # Load existing state
        ctx.load()
        
        # Update state
        ctx.update_task("Build scanner", "active", "completed")
        ctx.add_learning("API rate limits require caching")
        ctx.record_decision(...)
        
        # Save state
        ctx.save()
        
        # Generate wake-up prompt
        prompt = ctx.generate_wakeup_prompt()
    """
    
    def __init__(self, dna_path: str):
        self.dna_path = Path(dna_path)
        self.identity = IdentityState(role="", style="")
        self.project = ProjectState()
        self.knowledge = KnowledgeState()
        self.decisions: List[Decision] = []
        self.changelog: List[StateChange] = []
        self.mission: Dict[str, Any] = {}
        self.tactical: Dict[str, Any] = {}
    
    def load(self) -> bool:
        """Load state from DNA document"""
        if not self.dna_path.exists():
            return False
        
        with open(self.dna_path, 'r') as f:
            data = json.load(f)
        
        # Load identity
        if 'identity' in data:
            self.identity = IdentityState(**data['identity'])
        
        # Load project state
        if 'project' in data:
            self.project = ProjectState(**data['project'])
        
        # Load knowledge
        if 'knowledge' in data:
            self.knowledge = KnowledgeState(**data['knowledge'])
        
        # Load decisions
        if 'decisions' in data:
            self.decisions = [Decision(**d) for d in data['decisions']]
        
        # Load other sections
        self.mission = data.get('mission', {})
        self.tactical = data.get('tactical', {})
        self.changelog = [StateChange(**c) for c in data.get('changelog', [])]
        
        return True
    
    def save(self):
        """Persist current state to DNA document"""
        data = {
            'identity': {
                'role': self.identity.role,
                'style': self.identity.style,
                'constraints': self.identity.constraints,
                'domain_expertise': self.identity.domain_expertise
            },
            'project': {
                'active_tasks': self.project.active_tasks,
                'completed_tasks': self.project.completed_tasks,
                'blocked_tasks': self.project.blocked_tasks,
                'open_questions': self.project.open_questions
            },
            'knowledge': {
                'successful_patterns': self.knowledge.successful_patterns,
                'failed_approaches': self.knowledge.failed_approaches,
                'domain_insights': self.knowledge.domain_insights
            },
            'decisions': [
                {
                    'timestamp': d.timestamp,
                    'title': d.title,
                    'choice': d.choice,
                    'options_considered': d.options_considered,
                    'rationale': d.rationale
                }
                for d in self.decisions
            ],
            'mission': self.mission,
            'tactical': self.tactical,
            'changelog': [
                {
                    'timestamp': c.timestamp,
                    'category': c.category,
                    'key': c.key,
                    'from_value': c.from_value,
                    'to_value': c.to_value,
                    'reason': c.reason
                }
                for c in self.changelog
            ],
            'last_updated': datetime.now().isoformat()
        }
        
        self.dna_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.dna_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_task(self, task: str, from_state: str, to_state: str, reason: str = ""):
        """Move a task between states"""
        state_lists = {
            'active': self.project.active_tasks,
            'completed': self.project.completed_tasks,
            'blocked': self.project.blocked_tasks
        }
        
        # Remove from old state
        if from_state in state_lists and task in state_lists[from_state]:
            state_lists[from_state].remove(task)
        
        # Add to new state
        if to_state in state_lists and task not in state_lists[to_state]:
            state_lists[to_state].append(task)
        
        # Log the change
        self._log_change('project', f'task:{task}', from_state, to_state, reason)
    
    def add_task(self, task: str, state: str = 'active'):
        """Add a new task"""
        state_lists = {
            'active': self.project.active_tasks,
            'completed': self.project.completed_tasks,
            'blocked': self.project.blocked_tasks
        }
        
        if state in state_lists and task not in state_lists[state]:
            state_lists[state].append(task)
            self._log_change('project', f'task:{task}', None, state, 'New task added')
    
    def add_learning(self, insight: str, category: str = 'insights'):
        """Record a new learning"""
        lists = {
            'successful': self.knowledge.successful_patterns,
            'failed': self.knowledge.failed_approaches,
            'insights': self.knowledge.domain_insights
        }
        
        if category in lists and insight not in lists[category]:
            lists[category].append(insight)
            self._log_change('knowledge', category, None, insight, 'Learning recorded')
    
    def record_decision(self, title: str, choice: str, 
                       options: List[str], rationale: str):
        """Record a decision with full context"""
        decision = Decision(
            timestamp=datetime.now().isoformat(),
            title=title,
            choice=choice,
            options_considered=options,
            rationale=rationale
        )
        self.decisions.append(decision)
        self._log_change('decisions', title, None, choice, rationale)
    
    def _log_change(self, category: str, key: str, 
                   from_value: Any, to_value: Any, reason: str):
        """Internal: record a state change"""
        change = StateChange(
            timestamp=datetime.now().isoformat(),
            category=category,
            key=key,
            from_value=from_value,
            to_value=to_value,
            reason=reason
        )
        self.changelog.append(change)
    
    def generate_wakeup_prompt(self) -> str:
        """Generate a wake-up prompt for session initialization"""
        prompt_parts = []
        
        # Identity section
        prompt_parts.append("## Identity")
        prompt_parts.append(f"You are {self.identity.role}.")
        prompt_parts.append(f"Communication style: {self.identity.style}")
        if self.identity.constraints:
            prompt_parts.append(f"Constraints: {', '.join(self.identity.constraints)}")
        prompt_parts.append("")
        
        # Current state section
        prompt_parts.append("## Current State")
        if self.project.active_tasks:
            prompt_parts.append(f"Active tasks: {', '.join(self.project.active_tasks)}")
        if self.project.blocked_tasks:
            prompt_parts.append(f"Blocked: {', '.join(self.project.blocked_tasks)}")
        if self.project.completed_tasks:
            recent = self.project.completed_tasks[-3:]  # Last 3
            prompt_parts.append(f"Recently completed: {', '.join(recent)}")
        prompt_parts.append("")
        
        # Knowledge section
        prompt_parts.append("## Key Knowledge")
        if self.knowledge.successful_patterns:
            prompt_parts.append("What works:")
            for pattern in self.knowledge.successful_patterns[-5:]:
                prompt_parts.append(f"  - {pattern}")
        if self.knowledge.domain_insights:
            prompt_parts.append("Key insights:")
            for insight in self.knowledge.domain_insights[-5:]:
                prompt_parts.append(f"  - {insight}")
        prompt_parts.append("")
        
        # Mission section
        if self.mission:
            prompt_parts.append("## Mission")
            for key, value in self.mission.items():
                prompt_parts.append(f"{key}: {value}")
            prompt_parts.append("")
        
        # Tactical section
        if self.tactical:
            prompt_parts.append("## Immediate Focus")
            for key, value in self.tactical.items():
                prompt_parts.append(f"{key}: {value}")
        
        return "\n".join(prompt_parts)
    
    def generate_summary(self) -> str:
        """Generate a session summary"""
        summary_parts = []
        
        summary_parts.append(f"# Session Summary — {datetime.now().strftime('%Y-%m-%d')}")
        summary_parts.append("")
        
        # Recent completions
        if self.project.completed_tasks:
            summary_parts.append("## Completed")
            for task in self.project.completed_tasks[-5:]:
                summary_parts.append(f"- {task}")
            summary_parts.append("")
        
        # Recent decisions
        if self.decisions:
            summary_parts.append("## Decisions Made")
            for decision in self.decisions[-3:]:
                summary_parts.append(f"- **{decision.title}:** {decision.choice}")
                summary_parts.append(f"  Rationale: {decision.rationale}")
            summary_parts.append("")
        
        # Current state
        summary_parts.append("## Current State")
        if self.project.active_tasks:
            summary_parts.append(f"Active: {', '.join(self.project.active_tasks)}")
        if self.project.blocked_tasks:
            summary_parts.append(f"Blocked: {', '.join(self.project.blocked_tasks)}")
        summary_parts.append("")
        
        # Next session
        summary_parts.append("## Next Session")
        if self.tactical.get('priority'):
            summary_parts.append(f"Priority: {self.tactical['priority']}")
        if self.project.open_questions:
            summary_parts.append("Open questions:")
            for q in self.project.open_questions:
                summary_parts.append(f"  - {q}")
        
        return "\n".join(summary_parts)


# Example usage
if __name__ == "__main__":
    # Initialize context manager
    ctx = ContextManager("example_dna.json")
    
    # Set up identity
    ctx.identity.role = "an AI assistant for data analysis"
    ctx.identity.style = "concise and technical"
    ctx.identity.constraints = ["focus on actionable insights", "cite sources"]
    
    # Set mission
    ctx.mission = {
        "objective": "Build comprehensive analysis tools",
        "success_criteria": "Tools that surface patterns automatically"
    }
    
    # Add some tasks
    ctx.add_task("Build data scanner", "active")
    ctx.add_task("Create dashboard", "active")
    ctx.add_task("Write documentation", "active")
    
    # Record a learning
    ctx.add_learning("API rate limits require caching for efficiency")
    
    # Complete a task
    ctx.update_task("Build data scanner", "active", "completed", 
                   "Scanner implemented and tested")
    
    # Record a decision
    ctx.record_decision(
        title="Framework Choice",
        choice="Python + pandas",
        options=["Python + pandas", "R + tidyverse", "JavaScript"],
        rationale="Best ecosystem for financial data analysis"
    )
    
    # Set tactical focus
    ctx.tactical = {
        "priority": "Complete dashboard",
        "next_action": "Add visualization components"
    }
    
    # Save state
    ctx.save()
    print("State saved to example_dna.json")
    
    # Generate wake-up prompt
    print("\n" + "="*50)
    print("WAKE-UP PROMPT:")
    print("="*50)
    print(ctx.generate_wakeup_prompt())
    
    # Generate summary
    print("\n" + "="*50)
    print("SESSION SUMMARY:")
    print("="*50)
    print(ctx.generate_summary())
