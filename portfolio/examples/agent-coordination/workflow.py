"""
Multi-Agent Workflow Example
============================
Demonstrates coordination between Research and Builder agents.

This shows:
1. Task routing based on content
2. Handoff document generation
3. Status tracking across agents
4. Decision escalation patterns
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class AgentType(Enum):
    RESEARCH = "research"
    BUILDER = "builder"
    HUMAN = "human"


class WorkflowStage(Enum):
    PLANNING = "planning"
    RESEARCH = "research"
    BUILDING = "building"
    REVIEW = "review"
    COMPLETE = "complete"


class MultiAgentWorkflow:
    """
    Orchestrates work between multiple AI agents.
    
    Workflow pattern:
    1. Human defines objective
    2. Research agent analyzes and plans
    3. Builder agent implements
    4. Human reviews
    5. Iterate as needed
    """
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.stage = WorkflowStage.PLANNING
        self.tasks: List[Dict[str, Any]] = []
        self.handoffs: List[Dict[str, Any]] = []
        self.decisions: List[Dict[str, Any]] = []
        self.log: List[Dict[str, Any]] = []
    
    def _log(self, agent: AgentType, action: str, details: str = ""):
        """Internal logging"""
        self.log.append({
            'timestamp': datetime.now().isoformat(),
            'agent': agent.value,
            'action': action,
            'details': details
        })
    
    def add_task(self, description: str, assigned_to: AgentType):
        """Add a task to the workflow"""
        task = {
            'id': len(self.tasks) + 1,
            'description': description,
            'assigned_to': assigned_to.value,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        self.tasks.append(task)
        self._log(AgentType.HUMAN, 'task_created', description)
        return task['id']
    
    def route_task(self, description: str) -> AgentType:
        """
        Automatically route a task to appropriate agent.
        
        Research tasks → Research agent
        Implementation tasks → Builder agent
        Decision tasks → Human
        """
        desc_lower = description.lower()
        
        # Research indicators
        research_keywords = [
            'analyze', 'research', 'investigate', 'compare',
            'evaluate', 'why', 'strategy', 'plan', 'design'
        ]
        if any(kw in desc_lower for kw in research_keywords):
            return AgentType.RESEARCH
        
        # Builder indicators
        build_keywords = [
            'build', 'create', 'write', 'implement', 'code',
            'fix', 'deploy', 'run', 'test', 'script'
        ]
        if any(kw in desc_lower for kw in build_keywords):
            return AgentType.BUILDER
        
        # Human decision indicators
        decision_keywords = [
            'decide', 'choose', 'approve', 'priority',
            'should we', 'budget', 'timeline'
        ]
        if any(kw in desc_lower for kw in decision_keywords):
            return AgentType.HUMAN
        
        # Default to research for ambiguous tasks
        return AgentType.RESEARCH
    
    def create_handoff(
        self,
        from_agent: AgentType,
        to_agent: AgentType,
        context: str,
        deliverable: str,
        constraints: List[str]
    ) -> str:
        """
        Create a handoff document for passing work between agents.
        
        Returns formatted handoff document.
        """
        handoff = {
            'id': len(self.handoffs) + 1,
            'from': from_agent.value,
            'to': to_agent.value,
            'context': context,
            'deliverable': deliverable,
            'constraints': constraints,
            'timestamp': datetime.now().isoformat()
        }
        self.handoffs.append(handoff)
        self._log(from_agent, 'handoff_created', f'to {to_agent.value}')
        
        # Generate formatted document
        lines = [
            f"# Handoff: {from_agent.value.title()} → {to_agent.value.title()}",
            f"*{datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
            "## Context",
            context,
            "",
            "## Your Task",
            deliverable,
            "",
            "## Constraints"
        ]
        
        for c in constraints:
            lines.append(f"- {c}")
        
        return "\n".join(lines)
    
    def request_decision(
        self,
        context: str,
        options: List[Dict[str, Any]],
        recommendation: Optional[str] = None
    ) -> str:
        """
        Create a decision request for human orchestrator.
        
        Returns formatted decision request.
        """
        decision_req = {
            'id': len(self.decisions) + 1,
            'context': context,
            'options': options,
            'recommendation': recommendation,
            'status': 'pending',
            'timestamp': datetime.now().isoformat()
        }
        self.decisions.append(decision_req)
        self._log(AgentType.RESEARCH, 'decision_requested', context[:50])
        
        # Generate formatted document
        lines = [
            "# Decision Needed",
            "",
            "## Context",
            context,
            "",
            "## Options"
        ]
        
        for i, opt in enumerate(options, 1):
            lines.append(f"")
            lines.append(f"### Option {i}: {opt['name']}")
            lines.append("")
            if 'pros' in opt:
                lines.append("**Pros:**")
                for pro in opt['pros']:
                    lines.append(f"- {pro}")
            if 'cons' in opt:
                lines.append("")
                lines.append("**Cons:**")
                for con in opt['cons']:
                    lines.append(f"- {con}")
        
        if recommendation:
            lines.extend([
                "",
                "## Recommendation",
                f"**{recommendation}**"
            ])
        
        return "\n".join(lines)
    
    def update_task_status(self, task_id: int, status: str, notes: str = ""):
        """Update status of a task"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = status
                if notes:
                    task['notes'] = notes
                task['updated_at'] = datetime.now().isoformat()
                
                agent = AgentType(task['assigned_to'])
                self._log(agent, 'task_updated', f'{status}: {notes}')
                break
    
    def advance_stage(self):
        """Move workflow to next stage"""
        stages = list(WorkflowStage)
        current_idx = stages.index(self.stage)
        
        if current_idx < len(stages) - 1:
            self.stage = stages[current_idx + 1]
            self._log(AgentType.HUMAN, 'stage_advanced', self.stage.value)
    
    def get_status(self) -> str:
        """Generate current workflow status"""
        pending = [t for t in self.tasks if t['status'] == 'pending']
        in_progress = [t for t in self.tasks if t['status'] == 'in_progress']
        completed = [t for t in self.tasks if t['status'] == 'completed']
        
        lines = [
            f"# {self.project_name} - Workflow Status",
            f"*Stage: {self.stage.value}*",
            "",
            "## Tasks",
            f"- Pending: {len(pending)}",
            f"- In Progress: {len(in_progress)}",
            f"- Completed: {len(completed)}",
            "",
            "### Active Tasks"
        ]
        
        for task in in_progress:
            lines.append(f"- [{task['assigned_to']}] {task['description']}")
        
        lines.extend([
            "",
            "## Pending Decisions",
            f"Count: {len([d for d in self.decisions if d['status'] == 'pending'])}"
        ])
        
        return "\n".join(lines)
    
    def export(self, path: str):
        """Export workflow state"""
        data = {
            'project': self.project_name,
            'stage': self.stage.value,
            'tasks': self.tasks,
            'handoffs': self.handoffs,
            'decisions': self.decisions,
            'log': self.log,
            'exported_at': datetime.now().isoformat()
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


def example_workflow():
    """
    Demonstrate a complete multi-agent workflow.
    """
    print("=" * 60)
    print("MULTI-AGENT WORKFLOW DEMONSTRATION")
    print("=" * 60)
    print()
    
    # Initialize workflow
    workflow = MultiAgentWorkflow("Data Analysis Platform")
    
    # Phase 1: Human defines objective
    print("## Phase 1: Human Defines Objective\n")
    
    task_descriptions = [
        "Research best approaches for pattern detection in time series",
        "Build a Python scanner that implements the chosen approach",
        "Decide on deployment platform: cloud vs local",
        "Create documentation for the scanner"
    ]
    
    for desc in task_descriptions:
        agent = workflow.route_task(desc)
        task_id = workflow.add_task(desc, agent)
        print(f"Task {task_id}: {desc}")
        print(f"  → Routed to: {agent.value}")
    
    print()
    workflow.advance_stage()  # → RESEARCH
    
    # Phase 2: Research agent works
    print("## Phase 2: Research Agent Analysis\n")
    
    # Simulate research completion
    workflow.update_task_status(1, 'completed', 
        'Analyzed 3 approaches: moving averages, statistical methods, ML')
    
    # Create handoff to builder
    handoff = workflow.create_handoff(
        from_agent=AgentType.RESEARCH,
        to_agent=AgentType.BUILDER,
        context="Analysis complete. Recommending statistical approach with "
                "z-score deviation detection. Simpler than ML, more robust than MA.",
        deliverable="Build Python scanner with:\n"
                   "1. Data fetching from API\n"
                   "2. Z-score calculation\n"
                   "3. Pattern classification\n"
                   "4. Ranked output",
        constraints=[
            "Use only standard libraries + pandas",
            "Include CLI interface",
            "Output JSON format"
        ]
    )
    
    print("Research → Builder Handoff Created:")
    print("-" * 40)
    print(handoff)
    print()
    
    workflow.advance_stage()  # → BUILDING
    
    # Phase 3: Decision request
    print("## Phase 3: Decision Request\n")
    
    decision = workflow.request_decision(
        context="Scanner is ready for deployment. Need to decide on platform.",
        options=[
            {
                'name': 'Local Execution',
                'pros': ['Simple setup', 'No ongoing costs', 'Full control'],
                'cons': ['Manual execution', 'No mobile access']
            },
            {
                'name': 'Cloud Deployment',
                'pros': ['Automated scheduling', 'Access anywhere'],
                'cons': ['Monthly costs', 'More complexity']
            }
        ],
        recommendation="Local Execution for MVP, migrate to cloud after validation"
    )
    
    print("Decision Request:")
    print("-" * 40)
    print(decision)
    print()
    
    # Phase 4: Status check
    print("## Workflow Status\n")
    print(workflow.get_status())
    
    # Export
    workflow.export("workflow_example.json")
    print("\nWorkflow exported to workflow_example.json")


if __name__ == "__main__":
    example_workflow()
