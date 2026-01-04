"""
Wake-Up Protocol Example
========================
Demonstrates session initialization with prior context.

This shows how to:
1. Load previous session state
2. Generate wake-up prompts
3. Initialize AI with continuity
4. Handle cold starts
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class WakeUpProtocol:
    """
    Manages session initialization with prior context.
    
    The wake-up protocol ensures AI sessions start with:
    - Identity (who am I in this context)
    - State (what's the current situation)
    - History (what happened before)
    - Mission (what are we trying to achieve)
    - Tactical (what's the immediate focus)
    """
    
    def __init__(self, dna_path: str):
        self.dna_path = Path(dna_path)
        self.context: Dict[str, Any] = {}
    
    def load_context(self) -> bool:
        """Load context from DNA document"""
        if not self.dna_path.exists():
            return False
        
        with open(self.dna_path, 'r') as f:
            self.context = json.load(f)
        return True
    
    def generate_identity_section(self) -> str:
        """Generate identity portion of wake-up prompt"""
        identity = self.context.get('identity', {})
        
        lines = [
            "## Identity",
            "",
            f"You are {identity.get('role', 'an AI assistant')}.",
            "",
            f"**Communication style:** {identity.get('style', 'helpful and clear')}",
        ]
        
        constraints = identity.get('constraints', [])
        if constraints:
            lines.append("")
            lines.append("**Constraints:**")
            for c in constraints:
                lines.append(f"- {c}")
        
        return "\n".join(lines)
    
    def generate_state_section(self) -> str:
        """Generate current state portion of wake-up prompt"""
        project = self.context.get('project', {})
        
        lines = ["## Current State", ""]
        
        # Active work
        active = project.get('active_tasks', [])
        if active:
            lines.append("**Active tasks:**")
            for task in active:
                lines.append(f"- {task}")
            lines.append("")
        
        # Completed (recent only)
        completed = project.get('completed_tasks', [])
        if completed:
            recent = completed[-3:]  # Last 3
            lines.append("**Recently completed:**")
            for task in recent:
                lines.append(f"- ✓ {task}")
            lines.append("")
        
        # Blocked
        blocked = project.get('blocked_tasks', [])
        if blocked:
            lines.append("**Blocked:**")
            for task in blocked:
                lines.append(f"- ⚠️ {task}")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_history_section(self) -> str:
        """Generate history portion of wake-up prompt"""
        knowledge = self.context.get('knowledge', {})
        decisions = self.context.get('decisions', [])
        
        lines = ["## History", ""]
        
        # Key learnings
        insights = knowledge.get('domain_insights', [])
        if insights:
            lines.append("**Key learnings:**")
            for insight in insights[-5:]:  # Last 5
                lines.append(f"- {insight}")
            lines.append("")
        
        # Recent decisions
        if decisions:
            lines.append("**Recent decisions:**")
            for decision in decisions[-3:]:  # Last 3
                lines.append(f"- **{decision.get('title')}:** {decision.get('choice')}")
                if decision.get('rationale'):
                    lines.append(f"  - Why: {decision['rationale']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_mission_section(self) -> str:
        """Generate mission portion of wake-up prompt"""
        mission = self.context.get('mission', {})
        
        if not mission:
            return ""
        
        lines = ["## Mission", ""]
        
        objective = mission.get('objective')
        if objective:
            lines.append(f"**Primary objective:** {objective}")
            lines.append("")
        
        criteria = mission.get('success_criteria')
        if criteria:
            lines.append(f"**Success criteria:** {criteria}")
            lines.append("")
        
        values = mission.get('values', [])
        if values:
            lines.append("**Values:**")
            for value in values:
                lines.append(f"- {value}")
        
        return "\n".join(lines)
    
    def generate_tactical_section(self) -> str:
        """Generate tactical portion of wake-up prompt"""
        tactical = self.context.get('tactical', {})
        
        if not tactical:
            return ""
        
        lines = ["## Today's Focus", ""]
        
        priority = tactical.get('priority')
        if priority:
            lines.append(f"**Priority:** {priority}")
            lines.append("")
        
        next_action = tactical.get('next_action')
        if next_action:
            lines.append(f"**Next action:** {next_action}")
            lines.append("")
        
        questions = self.context.get('project', {}).get('open_questions', [])
        if questions:
            lines.append("**Open questions:**")
            for q in questions:
                lines.append(f"- {q}")
        
        return "\n".join(lines)
    
    def generate_full_wakeup(self, session_focus: str = "") -> str:
        """
        Generate complete wake-up prompt.
        
        Args:
            session_focus: Specific focus for this session (optional)
        
        Returns:
            Complete wake-up prompt ready to use
        """
        sections = [
            "# Session Initialization",
            f"*Loaded: {datetime.now().isoformat()}*",
            "",
            self.generate_identity_section(),
            "",
            self.generate_state_section(),
            self.generate_history_section(),
            self.generate_mission_section(),
            self.generate_tactical_section()
        ]
        
        if session_focus:
            sections.extend([
                "",
                "---",
                "",
                "## This Session",
                f"**Focus:** {session_focus}"
            ])
        
        return "\n".join(sections)
    
    def generate_minimal_wakeup(self) -> str:
        """
        Generate minimal wake-up for quick sessions.
        
        Just identity, current state, and immediate focus.
        """
        identity = self.context.get('identity', {})
        project = self.context.get('project', {})
        tactical = self.context.get('tactical', {})
        
        lines = [
            f"You are {identity.get('role', 'an AI assistant')}. "
            f"Style: {identity.get('style', 'helpful')}.",
            "",
            f"Current active tasks: {', '.join(project.get('active_tasks', ['none']))}",
            "",
            f"Today's priority: {tactical.get('priority', 'Continue current work')}"
        ]
        
        return "\n".join(lines)
    
    def cold_start_prompt(self) -> str:
        """
        Generate prompt for when no prior context exists.
        
        Asks user to provide essential context.
        """
        return """# New Session - No Prior Context Found

I don't have any prior context loaded. To work effectively, please provide:

## Required
1. **What project are we working on?**
2. **What's your role/goal?**
3. **What should I focus on today?**

## Optional but Helpful
- Recent progress or decisions
- Known constraints or requirements
- Any relevant background

Once you provide this, I'll be ready to assist."""


# Utility function for common use case
def initialize_session(dna_path: str, focus: str = "") -> str:
    """
    Convenience function to initialize a session.
    
    Args:
        dna_path: Path to DNA document
        focus: Optional specific focus for session
    
    Returns:
        Ready-to-use wake-up prompt
    """
    protocol = WakeUpProtocol(dna_path)
    
    if protocol.load_context():
        return protocol.generate_full_wakeup(focus)
    else:
        return protocol.cold_start_prompt()


# Example usage
if __name__ == "__main__":
    # Create sample DNA document
    sample_dna = {
        "identity": {
            "role": "an AI assistant helping build a data analysis platform",
            "style": "technical but approachable, concise, action-oriented",
            "constraints": [
                "Focus on actionable outputs",
                "Cite sources when making claims",
                "Ask clarifying questions when requirements are unclear"
            ]
        },
        "project": {
            "active_tasks": [
                "Build pattern scanner",
                "Create visualization dashboard",
                "Write documentation"
            ],
            "completed_tasks": [
                "Set up project structure",
                "Implement data fetching",
                "Define scoring algorithm"
            ],
            "blocked_tasks": [],
            "open_questions": [
                "Should we add real-time updates?",
                "What's the deployment target?"
            ]
        },
        "knowledge": {
            "successful_patterns": [
                "CLI tools work better than GUIs for iteration speed",
                "Multi-factor scoring reduces false positives"
            ],
            "failed_approaches": [
                "Single-factor scoring missed important nuance"
            ],
            "domain_insights": [
                "Rate limiting requires caching strategy",
                "Users prefer ranked lists over raw data"
            ]
        },
        "decisions": [
            {
                "title": "Framework Choice",
                "choice": "Python + pandas",
                "rationale": "Best ecosystem for data analysis"
            },
            {
                "title": "Output Format",
                "choice": "JSON with optional Markdown report",
                "rationale": "Flexible for different consumers"
            }
        ],
        "mission": {
            "objective": "Build tools that surface actionable patterns from data",
            "success_criteria": "Users can identify opportunities in < 5 minutes",
            "values": [
                "Accuracy over speed",
                "Simplicity over features"
            ]
        },
        "tactical": {
            "priority": "Complete the pattern scanner",
            "next_action": "Add visualization to output"
        }
    }
    
    # Save sample DNA
    dna_path = "sample_dna.json"
    with open(dna_path, 'w') as f:
        json.dump(sample_dna, f, indent=2)
    
    # Generate wake-up prompts
    protocol = WakeUpProtocol(dna_path)
    protocol.load_context()
    
    print("=" * 60)
    print("FULL WAKE-UP PROMPT")
    print("=" * 60)
    print(protocol.generate_full_wakeup("Finish the pattern scanner"))
    
    print("\n" + "=" * 60)
    print("MINIMAL WAKE-UP PROMPT")
    print("=" * 60)
    print(protocol.generate_minimal_wakeup())
    
    print("\n" + "=" * 60)
    print("COLD START PROMPT")
    print("=" * 60)
    print(protocol.cold_start_prompt())
    
    # Cleanup
    Path(dna_path).unlink()
