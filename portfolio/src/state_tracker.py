"""
State Tracker
=============
Utilities for tracking and persisting state across sessions.

This module provides:
- State snapshots and restoration
- Change tracking with audit trail
- State diffing and merging
- Export/import functionality
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from copy import deepcopy


@dataclass
class StateSnapshot:
    """A point-in-time capture of state"""
    timestamp: str
    state: Dict[str, Any]
    checksum: str
    description: str


@dataclass
class StateDiff:
    """Difference between two states"""
    from_timestamp: str
    to_timestamp: str
    added: Dict[str, Any]
    removed: Dict[str, Any]
    changed: Dict[str, Dict[str, Any]]  # key: {"from": ..., "to": ...}


class StateTracker:
    """
    Track state changes across sessions with full audit trail.
    
    Features:
    - Automatic snapshots
    - Change detection
    - Rollback capability
    - Export/import
    
    Usage:
        tracker = StateTracker("state_history.json")
        
        # Initialize with state
        tracker.set_state({"tasks": ["Build scanner"], "status": "active"})
        
        # Update and track changes
        tracker.update("status", "completed")
        
        # View history
        history = tracker.get_history()
        
        # Rollback if needed
        tracker.rollback(steps=1)
        
        # Export
        tracker.export("backup.json")
    """
    
    def __init__(self, history_path: Optional[str] = None):
        self.history_path = Path(history_path) if history_path else None
        self.current_state: Dict[str, Any] = {}
        self.snapshots: List[StateSnapshot] = []
        self.change_log: List[Dict[str, Any]] = []
        
        if self.history_path and self.history_path.exists():
            self._load_history()
    
    def _compute_checksum(self, state: Dict[str, Any]) -> str:
        """Compute checksum for state integrity verification"""
        state_str = json.dumps(state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]
    
    def _load_history(self):
        """Load state history from file"""
        with open(self.history_path, 'r') as f:
            data = json.load(f)
        
        self.snapshots = [
            StateSnapshot(**s) for s in data.get('snapshots', [])
        ]
        self.change_log = data.get('change_log', [])
        
        if self.snapshots:
            self.current_state = deepcopy(self.snapshots[-1].state)
    
    def _save_history(self):
        """Persist state history to file"""
        if not self.history_path:
            return
        
        data = {
            'snapshots': [asdict(s) for s in self.snapshots],
            'change_log': self.change_log,
            'last_updated': datetime.now().isoformat()
        }
        
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def set_state(self, state: Dict[str, Any], description: str = "Initial state"):
        """Set the current state (creates snapshot)"""
        self.current_state = deepcopy(state)
        self._create_snapshot(description)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state"""
        return deepcopy(self.current_state)
    
    def update(self, key: str, value: Any, reason: str = ""):
        """Update a single value and track the change"""
        old_value = self.current_state.get(key)
        self.current_state[key] = value
        
        self.change_log.append({
            'timestamp': datetime.now().isoformat(),
            'key': key,
            'from': old_value,
            'to': value,
            'reason': reason
        })
        
        self._save_history()
    
    def update_nested(self, path: List[str], value: Any, reason: str = ""):
        """Update a nested value using path like ["tasks", "active", 0]"""
        # Navigate to parent
        current = self.current_state
        old_value = None
        
        for key in path[:-1]:
            if isinstance(current, dict):
                current = current.setdefault(key, {})
            elif isinstance(current, list):
                current = current[int(key)]
        
        # Update final key
        final_key = path[-1]
        if isinstance(current, dict):
            old_value = current.get(final_key)
            current[final_key] = value
        elif isinstance(current, list):
            idx = int(final_key)
            old_value = current[idx] if idx < len(current) else None
            if idx < len(current):
                current[idx] = value
            else:
                current.append(value)
        
        self.change_log.append({
            'timestamp': datetime.now().isoformat(),
            'path': '.'.join(str(p) for p in path),
            'from': old_value,
            'to': value,
            'reason': reason
        })
        
        self._save_history()
    
    def _create_snapshot(self, description: str):
        """Create a state snapshot"""
        snapshot = StateSnapshot(
            timestamp=datetime.now().isoformat(),
            state=deepcopy(self.current_state),
            checksum=self._compute_checksum(self.current_state),
            description=description
        )
        self.snapshots.append(snapshot)
        self._save_history()
    
    def snapshot(self, description: str = "Manual snapshot"):
        """Create a manual snapshot of current state"""
        self._create_snapshot(description)
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent state history"""
        recent = self.change_log[-limit:] if limit else self.change_log
        return [
            {
                'timestamp': c['timestamp'],
                'key': c.get('key') or c.get('path'),
                'change': f"{c['from']} → {c['to']}",
                'reason': c.get('reason', '')
            }
            for c in recent
        ]
    
    def diff(self, from_snapshot: int = -2, to_snapshot: int = -1) -> StateDiff:
        """
        Calculate difference between two snapshots.
        
        Args:
            from_snapshot: Index of starting snapshot (default: second to last)
            to_snapshot: Index of ending snapshot (default: last)
        
        Returns:
            StateDiff object with added, removed, and changed items
        """
        if len(self.snapshots) < 2:
            raise ValueError("Need at least 2 snapshots to diff")
        
        from_state = self.snapshots[from_snapshot].state
        to_state = self.snapshots[to_snapshot].state
        
        added = {}
        removed = {}
        changed = {}
        
        # Find added and changed
        for key, value in to_state.items():
            if key not in from_state:
                added[key] = value
            elif from_state[key] != value:
                changed[key] = {'from': from_state[key], 'to': value}
        
        # Find removed
        for key in from_state:
            if key not in to_state:
                removed[key] = from_state[key]
        
        return StateDiff(
            from_timestamp=self.snapshots[from_snapshot].timestamp,
            to_timestamp=self.snapshots[to_snapshot].timestamp,
            added=added,
            removed=removed,
            changed=changed
        )
    
    def rollback(self, steps: int = 1) -> bool:
        """
        Rollback to a previous snapshot.
        
        Args:
            steps: Number of snapshots to go back
        
        Returns:
            True if rollback succeeded
        """
        if steps >= len(self.snapshots):
            return False
        
        target_idx = -(steps + 1)
        target_snapshot = self.snapshots[target_idx]
        
        self.current_state = deepcopy(target_snapshot.state)
        
        # Remove newer snapshots
        self.snapshots = self.snapshots[:target_idx + 1]
        
        self.change_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'rollback',
            'to_timestamp': target_snapshot.timestamp,
            'reason': f'Rolled back {steps} step(s)'
        })
        
        self._save_history()
        return True
    
    def verify_integrity(self) -> bool:
        """Verify all snapshots have valid checksums"""
        for snapshot in self.snapshots:
            computed = self._compute_checksum(snapshot.state)
            if computed != snapshot.checksum:
                return False
        return True
    
    def export(self, path: str, include_history: bool = True):
        """Export state to file"""
        data = {
            'current_state': self.current_state,
            'exported_at': datetime.now().isoformat()
        }
        
        if include_history:
            data['snapshots'] = [asdict(s) for s in self.snapshots]
            data['change_log'] = self.change_log
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_state(self, path: str, merge: bool = False):
        """
        Import state from file.
        
        Args:
            path: File to import from
            merge: If True, merge with current state. If False, replace.
        """
        with open(path, 'r') as f:
            data = json.load(f)
        
        imported_state = data.get('current_state', data)
        
        if merge:
            self.current_state.update(imported_state)
        else:
            self.current_state = imported_state
        
        self._create_snapshot(f"Imported from {path}")
    
    def get_summary(self) -> str:
        """Generate human-readable state summary"""
        lines = [
            "# State Summary",
            f"*Generated: {datetime.now().isoformat()}*",
            "",
            f"**Snapshots:** {len(self.snapshots)}",
            f"**Changes tracked:** {len(self.change_log)}",
            f"**Integrity:** {'✓ Valid' if self.verify_integrity() else '✗ Invalid'}",
            "",
            "## Current State",
            "```json",
            json.dumps(self.current_state, indent=2),
            "```",
            "",
            "## Recent Changes"
        ]
        
        for change in self.get_history(5):
            lines.append(f"- **{change['key']}**: {change['change']}")
            if change['reason']:
                lines.append(f"  - Reason: {change['reason']}")
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    # Create tracker
    tracker = StateTracker("example_state_history.json")
    
    # Initialize state
    initial_state = {
        "project": "Data Analysis Tool",
        "phase": "development",
        "tasks": {
            "active": ["Build scanner", "Create dashboard"],
            "completed": [],
            "blocked": []
        },
        "metrics": {
            "items_analyzed": 0,
            "patterns_found": 0
        }
    }
    
    tracker.set_state(initial_state, "Project initialized")
    
    # Make some updates
    tracker.update("phase", "testing", "Scanner complete, moving to tests")
    
    tracker.update_nested(
        ["tasks", "completed"], 
        ["Build scanner"],
        "Scanner implemented and working"
    )
    
    tracker.update_nested(
        ["tasks", "active"],
        ["Create dashboard", "Write tests"],
        "Updated active tasks"
    )
    
    tracker.update_nested(
        ["metrics", "items_analyzed"],
        150,
        "First scan completed"
    )
    
    # Create explicit snapshot
    tracker.snapshot("End of day 1")
    
    # View history
    print("=== State History ===")
    for change in tracker.get_history():
        print(f"  {change['timestamp'][:19]}: {change['key']}")
        print(f"    {change['change']}")
        if change['reason']:
            print(f"    Reason: {change['reason']}")
    print()
    
    # View summary
    print("=== State Summary ===")
    print(tracker.get_summary())
    
    # Export
    tracker.export("state_backup.json")
    print("\nState exported to state_backup.json")
