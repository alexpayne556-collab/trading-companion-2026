"""
Agent Coordinator
=================
Utilities for coordinating multiple AI agents on shared tasks.

This module provides:
- Handoff protocol generation
- Status update formatting
- Decision request formatting
- Cross-agent context synchronization
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
import json


class AgentRole(Enum):
    """Defined agent roles in the system"""
    RESEARCH = "research"      # Deep analysis, strategy, reasoning
    BUILDER = "builder"        # Code, files, execution
    ORCHESTRATOR = "human"     # Decisions, QC, coordination


@dataclass
class AgentCapabilities:
    """What each agent role can do"""
    role: AgentRole
    strengths: List[str]
    limitations: List[str]
    best_for: List[str]


# Define standard agent capabilities
AGENT_PROFILES = {
    AgentRole.RESEARCH: AgentCapabilities(
        role=AgentRole.RESEARCH,
        strengths=[
            "Deep reasoning and analysis",
            "Pattern recognition",
            "Long-form thinking",
            "Strategy development",
            "Knowledge synthesis"
        ],
        limitations=[
            "Cannot execute code",
            "Cannot modify files",
            "Cannot run terminal commands"
        ],
        best_for=[
            "Complex analysis",
            "Strategic planning",
            "Research synthesis",
            "Problem decomposition"
        ]
    ),
    AgentRole.BUILDER: AgentCapabilities(
        role=AgentRole.BUILDER,
        strengths=[
            "Code generation",
            "File operations",
            "Terminal commands",
            "API integration",
            "Tool creation"
        ],
        limitations=[
            "Shorter context window",
            "Less suited for long reasoning chains"
        ],
        best_for=[
            "Implementation",
            "Tool building",
            "Automation",
            "File manipulation"
        ]
    ),
    AgentRole.ORCHESTRATOR: AgentCapabilities(
        role=AgentRole.ORCHESTRATOR,
        strengths=[
            "Judgment and intuition",
            "Decision authority",
            "Quality control",
            "Creative leaps",
            "Ethical judgment"
        ],
        limitations=[
            "Limited bandwidth",
            "Cannot scale infinitely"
        ],
        best_for=[
            "Final decisions",
            "Quality review",
            "Cross-agent coordination",
            "Priority setting"
        ]
    )
}


class HandoffProtocol:
    """Generate standardized handoff documents between agents"""
    
    @staticmethod
    def create_handoff(
        from_agent: AgentRole,
        to_agent: AgentRole,
        context: str,
        completed: List[str],
        task: str,
        constraints: List[str],
        expected_output: str
    ) -> str:
        """
        Generate a handoff document for passing work between agents.
        
        Args:
            from_agent: Who is handing off
            to_agent: Who is receiving
            context: Background information
            completed: What's been done so far
            task: Specific request for receiving agent
            constraints: Any limitations or requirements
            expected_output: What deliverable is needed
        
        Returns:
            Formatted handoff document
        """
        lines = [
            f"## Handoff: {from_agent.value.title()} → {to_agent.value.title()}",
            f"*Generated: {datetime.now().isoformat()}*",
            "",
            "### Context",
            context,
            "",
            "### Completed So Far"
        ]
        
        for item in completed:
            lines.append(f"- {item}")
        
        lines.extend([
            "",
            "### Your Task",
            task,
            "",
            "### Constraints"
        ])
        
        for constraint in constraints:
            lines.append(f"- {constraint}")
        
        lines.extend([
            "",
            "### Expected Output",
            expected_output
        ])
        
        return "\n".join(lines)


class StatusProtocol:
    """Generate standardized status updates"""
    
    @staticmethod
    def create_status(
        agent: AgentRole,
        completed: List[str],
        in_progress: List[str],
        blocked: List[Dict[str, str]],  # [{"item": ..., "blocker": ...}]
        next_steps: List[str]
    ) -> str:
        """
        Generate a status update document.
        
        Args:
            agent: Which agent is reporting
            completed: Finished items
            in_progress: Current work
            blocked: Items with blockers
            next_steps: Planned actions
        
        Returns:
            Formatted status document
        """
        lines = [
            f"## Status Update: {agent.value.title()} Agent",
            f"*Time: {datetime.now().isoformat()}*",
            "",
            "### Completed"
        ]
        
        for item in completed:
            lines.append(f"- ✅ {item}")
        
        lines.append("")
        lines.append("### In Progress")
        
        for item in in_progress:
            lines.append(f"- 🔄 {item}")
        
        if blocked:
            lines.append("")
            lines.append("### Blocked")
            for item in blocked:
                lines.append(f"- ⚠️ {item['item']}")
                lines.append(f"  - Blocker: {item['blocker']}")
        
        lines.append("")
        lines.append("### Next Steps")
        
        for step in next_steps:
            lines.append(f"1. {step}")
        
        return "\n".join(lines)


class DecisionProtocol:
    """Generate standardized decision requests"""
    
    @staticmethod
    def create_decision_request(
        context: str,
        options: List[Dict[str, Any]],  # [{"name": ..., "pros": [...], "cons": [...]}]
        recommendation: str,
        recommendation_rationale: str,
        delay_impact: str
    ) -> str:
        """
        Generate a decision request document.
        
        Args:
            context: Background on the situation
            options: Available choices with pros/cons
            recommendation: Which option is recommended
            recommendation_rationale: Why that option
            delay_impact: What happens if decision is delayed
        
        Returns:
            Formatted decision request
        """
        lines = [
            "## Decision Needed",
            f"*Requested: {datetime.now().isoformat()}*",
            "",
            "### Context",
            context,
            "",
            "### Options"
        ]
        
        for i, option in enumerate(options, 1):
            lines.append(f"")
            lines.append(f"**Option {i}: {option['name']}**")
            lines.append("")
            lines.append("Pros:")
            for pro in option.get('pros', []):
                lines.append(f"  - ✓ {pro}")
            lines.append("")
            lines.append("Cons:")
            for con in option.get('cons', []):
                lines.append(f"  - ✗ {con}")
        
        lines.extend([
            "",
            "### Recommendation",
            f"**{recommendation}**",
            "",
            f"Rationale: {recommendation_rationale}",
            "",
            "### Impact of Delay",
            delay_impact
        ])
        
        return "\n".join(lines)


class AgentCoordinator:
    """
    Central coordinator for multi-agent workflows.
    
    Usage:
        coord = AgentCoordinator()
        
        # Route task to appropriate agent
        agent = coord.route_task("Write Python scanner")
        
        # Generate handoff
        handoff = coord.handoff(
            from_agent=AgentRole.RESEARCH,
            to_agent=AgentRole.BUILDER,
            ...
        )
        
        # Request decision
        request = coord.request_decision(...)
    """
    
    def __init__(self):
        self.workflow_log: List[Dict] = []
    
    def route_task(self, task_description: str) -> AgentRole:
        """
        Determine which agent should handle a task.
        
        Args:
            task_description: What needs to be done
        
        Returns:
            Recommended agent role
        """
        task_lower = task_description.lower()
        
        # Code/implementation tasks → Builder
        code_keywords = ['write', 'code', 'implement', 'build', 'create file',
                        'python', 'script', 'tool', 'fix', 'debug', 'run']
        if any(kw in task_lower for kw in code_keywords):
            return AgentRole.BUILDER
        
        # Analysis/strategy tasks → Research
        research_keywords = ['analyze', 'research', 'strategy', 'why', 
                           'compare', 'evaluate', 'think', 'plan', 'design']
        if any(kw in task_lower for kw in research_keywords):
            return AgentRole.RESEARCH
        
        # Decision/approval tasks → Human
        decision_keywords = ['decide', 'approve', 'choose', 'review', 
                           'should we', 'priority', 'judgment']
        if any(kw in task_lower for kw in decision_keywords):
            return AgentRole.ORCHESTRATOR
        
        # Default to research for ambiguous tasks
        return AgentRole.RESEARCH
    
    def handoff(
        self,
        from_agent: AgentRole,
        to_agent: AgentRole,
        context: str,
        completed: List[str],
        task: str,
        constraints: List[str],
        expected_output: str
    ) -> str:
        """Create a handoff document and log it"""
        doc = HandoffProtocol.create_handoff(
            from_agent, to_agent, context, 
            completed, task, constraints, expected_output
        )
        
        self.workflow_log.append({
            'type': 'handoff',
            'timestamp': datetime.now().isoformat(),
            'from': from_agent.value,
            'to': to_agent.value,
            'task': task
        })
        
        return doc
    
    def status_update(
        self,
        agent: AgentRole,
        completed: List[str],
        in_progress: List[str],
        blocked: List[Dict[str, str]],
        next_steps: List[str]
    ) -> str:
        """Create a status update and log it"""
        doc = StatusProtocol.create_status(
            agent, completed, in_progress, blocked, next_steps
        )
        
        self.workflow_log.append({
            'type': 'status',
            'timestamp': datetime.now().isoformat(),
            'agent': agent.value,
            'completed_count': len(completed),
            'blocked_count': len(blocked)
        })
        
        return doc
    
    def request_decision(
        self,
        context: str,
        options: List[Dict[str, Any]],
        recommendation: str,
        rationale: str,
        delay_impact: str
    ) -> str:
        """Create a decision request and log it"""
        doc = DecisionProtocol.create_decision_request(
            context, options, recommendation, rationale, delay_impact
        )
        
        self.workflow_log.append({
            'type': 'decision_request',
            'timestamp': datetime.now().isoformat(),
            'options_count': len(options),
            'recommendation': recommendation
        })
        
        return doc
    
    def get_agent_profile(self, role: AgentRole) -> str:
        """Get a description of an agent's capabilities"""
        profile = AGENT_PROFILES[role]
        
        lines = [
            f"## {role.value.title()} Agent Profile",
            "",
            "### Strengths"
        ]
        
        for strength in profile.strengths:
            lines.append(f"- {strength}")
        
        lines.append("")
        lines.append("### Limitations")
        
        for limit in profile.limitations:
            lines.append(f"- {limit}")
        
        lines.append("")
        lines.append("### Best Used For")
        
        for use in profile.best_for:
            lines.append(f"- {use}")
        
        return "\n".join(lines)
    
    def export_workflow_log(self, path: str):
        """Export workflow log to JSON"""
        with open(path, 'w') as f:
            json.dump(self.workflow_log, f, indent=2)


# Example usage
if __name__ == "__main__":
    coord = AgentCoordinator()
    
    # Route some tasks
    print("=== Task Routing ===\n")
    tasks = [
        "Analyze the patterns in our data",
        "Write a Python script to scan the API",
        "Should we prioritize feature A or B?",
        "Build a dashboard for visualization"
    ]
    
    for task in tasks:
        agent = coord.route_task(task)
        print(f"Task: {task}")
        print(f"  → Route to: {agent.value.title()} Agent")
        print()
    
    # Generate a handoff
    print("=== Handoff Example ===\n")
    handoff = coord.handoff(
        from_agent=AgentRole.RESEARCH,
        to_agent=AgentRole.BUILDER,
        context="We've analyzed the requirements for a data scanner.",
        completed=[
            "Identified key metrics to track",
            "Defined scoring algorithm",
            "Specified output format"
        ],
        task="Implement a Python scanner that fetches data from the API, calculates scores, and outputs ranked results.",
        constraints=[
            "Use only free APIs",
            "Handle rate limiting gracefully",
            "Output in JSON format"
        ],
        expected_output="Working Python script with CLI interface"
    )
    print(handoff)
    
    # Generate a decision request
    print("\n=== Decision Request Example ===\n")
    decision = coord.request_decision(
        context="We need to choose a data storage approach for persisting analysis results.",
        options=[
            {
                "name": "JSON Files",
                "pros": ["Simple", "No dependencies", "Human readable"],
                "cons": ["Slower for large data", "No query capability"]
            },
            {
                "name": "SQLite Database",
                "pros": ["Fast queries", "SQL support", "Single file"],
                "cons": ["Requires schema", "More complexity"]
            }
        ],
        recommendation="JSON Files",
        rationale="Simplicity is more valuable than query speed for our use case. We can migrate to SQLite later if needed.",
        delay_impact="Implementation is blocked until we decide on storage format."
    )
    print(decision)
