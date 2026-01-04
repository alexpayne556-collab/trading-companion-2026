"""
Data Scanner Example
====================
Sanitized example showing the pattern scanner architecture.

This demonstrates:
- Multi-factor scoring systems
- Pattern detection
- Category-based analysis
- Ranked output generation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


@dataclass
class DataPoint:
    """A single item to analyze"""
    id: str
    category: str
    values: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScoredResult:
    """Analysis result with score"""
    item: DataPoint
    score: float
    pattern: str
    factors: Dict[str, float]
    summary: str


class PatternScanner:
    """
    Multi-factor pattern scanner.
    
    Analyzes data points and:
    1. Calculates scores based on multiple factors
    2. Detects pattern types
    3. Ranks and filters results
    4. Generates actionable output
    
    Usage:
        scanner = PatternScanner()
        
        # Add data
        scanner.add_data_point(DataPoint(...))
        
        # Run analysis
        results = scanner.scan()
        
        # Get top results
        top = scanner.get_top(n=10)
        
        # Export
        scanner.export("results.json")
    """
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.data_points: List[DataPoint] = []
        self.results: List[ScoredResult] = []
        
        # Default scoring weights (sum to 100)
        self.weights = weights or {
            'factor_a': 35,  # Primary signal
            'factor_b': 25,  # Secondary signal
            'factor_c': 25,  # Pattern quality
            'factor_d': 15   # Diversification
        }
    
    def add_data_point(self, point: DataPoint):
        """Add a data point to analyze"""
        self.data_points.append(point)
    
    def add_batch(self, points: List[DataPoint]):
        """Add multiple data points"""
        self.data_points.extend(points)
    
    def _calculate_factor_a(self, point: DataPoint) -> float:
        """
        Calculate primary signal score.
        Example: Momentum or trend strength.
        """
        value = point.values.get('signal_strength', 0)
        
        # Normalize to 0-35 range
        if value > 50:
            return 35
        elif value > 30:
            return 25
        elif value > 15:
            return 15
        else:
            return 5
    
    def _calculate_factor_b(self, point: DataPoint) -> float:
        """
        Calculate secondary signal score.
        Example: Independence from common factors.
        """
        # Higher independence = better diversification
        independence = point.values.get('independence', 0.5)
        
        # Normalize to 0-25 range
        return min(25, independence * 25)
    
    def _calculate_factor_c(self, point: DataPoint) -> float:
        """
        Calculate pattern quality score.
        Example: How clean/clear the pattern is.
        """
        quality = point.values.get('pattern_quality', 0.5)
        
        # Normalize to 0-25 range
        return min(25, quality * 25)
    
    def _calculate_factor_d(self, point: DataPoint) -> float:
        """
        Calculate diversification benefit.
        Example: Category representation.
        """
        # Count items in same category
        same_category = sum(
            1 for p in self.data_points 
            if p.category == point.category
        )
        
        # More unique = higher score
        if same_category == 1:
            return 15
        elif same_category <= 3:
            return 10
        elif same_category <= 5:
            return 5
        else:
            return 0
    
    def _detect_pattern(self, point: DataPoint) -> str:
        """
        Detect the pattern type for a data point.
        
        Returns pattern name based on characteristics.
        """
        values = point.values
        
        # Check for different pattern types
        if values.get('deviation_from_mean', 0) < -0.3:
            return "OVERSOLD"
        
        if values.get('pressure_ratio', 0) > 0.25:
            return "PRESSURE_BUILD"
        
        if values.get('relative_strength', 0) < 0.8:
            return "LAGGARD"
        
        if values.get('volume_trend', 0) > 1.5:
            return "ACCUMULATION"
        
        if values.get('breakout_signal', False):
            return "BREAKOUT"
        
        return "NEUTRAL"
    
    def _generate_summary(self, point: DataPoint, 
                         score: float, pattern: str) -> str:
        """Generate human-readable summary"""
        return (
            f"{point.id} ({point.category}): "
            f"Score {score:.0f}, Pattern: {pattern}"
        )
    
    def scan(self) -> List[ScoredResult]:
        """
        Run analysis on all data points.
        
        Returns list of scored results.
        """
        self.results = []
        
        for point in self.data_points:
            # Calculate all factors
            factors = {
                'factor_a': self._calculate_factor_a(point),
                'factor_b': self._calculate_factor_b(point),
                'factor_c': self._calculate_factor_c(point),
                'factor_d': self._calculate_factor_d(point)
            }
            
            # Total score
            score = sum(factors.values())
            
            # Detect pattern
            pattern = self._detect_pattern(point)
            
            # Generate summary
            summary = self._generate_summary(point, score, pattern)
            
            result = ScoredResult(
                item=point,
                score=score,
                pattern=pattern,
                factors=factors,
                summary=summary
            )
            
            self.results.append(result)
        
        # Sort by score
        self.results.sort(key=lambda x: x.score, reverse=True)
        
        return self.results
    
    def get_top(self, n: int = 10) -> List[ScoredResult]:
        """Get top N results by score"""
        return self.results[:n]
    
    def get_by_pattern(self, pattern: str) -> List[ScoredResult]:
        """Get all results matching a pattern"""
        return [r for r in self.results if r.pattern == pattern]
    
    def get_by_category(self, category: str) -> List[ScoredResult]:
        """Get all results in a category"""
        return [r for r in self.results if r.item.category == category]
    
    def get_diversified(self, n: int = 5) -> List[ScoredResult]:
        """
        Get top N results with category diversification.
        Each selected item must be from a different category.
        """
        selected = []
        used_categories = set()
        
        for result in self.results:
            if result.item.category not in used_categories:
                selected.append(result)
                used_categories.add(result.item.category)
                
                if len(selected) >= n:
                    break
        
        return selected
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get summary statistics"""
        if not self.results:
            return {}
        
        scores = [r.score for r in self.results]
        patterns = {}
        categories = {}
        
        for r in self.results:
            patterns[r.pattern] = patterns.get(r.pattern, 0) + 1
            categories[r.item.category] = categories.get(r.item.category, 0) + 1
        
        return {
            'total_items': len(self.results),
            'avg_score': sum(scores) / len(scores),
            'max_score': max(scores),
            'min_score': min(scores),
            'patterns': patterns,
            'categories': categories
        }
    
    def export(self, path: str):
        """Export results to JSON"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'results': [
                {
                    'id': r.item.id,
                    'category': r.item.category,
                    'score': r.score,
                    'pattern': r.pattern,
                    'factors': r.factors,
                    'summary': r.summary
                }
                for r in self.results
            ]
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_report(self) -> str:
        """Generate human-readable report"""
        lines = [
            "# Analysis Report",
            f"*Generated: {datetime.now().isoformat()}*",
            ""
        ]
        
        # Statistics
        stats = self.get_statistics()
        lines.extend([
            "## Summary Statistics",
            f"- Total items: {stats.get('total_items', 0)}",
            f"- Average score: {stats.get('avg_score', 0):.1f}",
            f"- Score range: {stats.get('min_score', 0):.0f} - {stats.get('max_score', 0):.0f}",
            ""
        ])
        
        # Pattern distribution
        lines.append("## Patterns Detected")
        for pattern, count in stats.get('patterns', {}).items():
            lines.append(f"- {pattern}: {count}")
        lines.append("")
        
        # Top results
        lines.append("## Top 10 Results")
        lines.append("")
        lines.append("| Rank | ID | Category | Score | Pattern |")
        lines.append("|------|-----|----------|-------|---------|")
        
        for i, result in enumerate(self.get_top(10), 1):
            lines.append(
                f"| {i} | {result.item.id} | {result.item.category} | "
                f"{result.score:.0f} | {result.pattern} |"
            )
        
        lines.append("")
        
        # Diversified selection
        lines.append("## Diversified Selection (Different Categories)")
        lines.append("")
        
        for i, result in enumerate(self.get_diversified(5), 1):
            lines.append(f"{i}. **{result.item.id}** ({result.item.category})")
            lines.append(f"   - Score: {result.score:.0f}")
            lines.append(f"   - Pattern: {result.pattern}")
            lines.append("")
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    # Create scanner
    scanner = PatternScanner()
    
    # Add sample data points
    sample_data = [
        DataPoint(
            id="ITEM_001",
            category="TECH",
            values={
                'signal_strength': 45,
                'independence': 0.8,
                'pattern_quality': 0.9,
                'deviation_from_mean': -0.35,
                'pressure_ratio': 0.22
            }
        ),
        DataPoint(
            id="ITEM_002",
            category="ENERGY",
            values={
                'signal_strength': 55,
                'independence': 0.7,
                'pattern_quality': 0.8,
                'deviation_from_mean': -0.41,
                'pressure_ratio': 0.32
            }
        ),
        DataPoint(
            id="ITEM_003",
            category="TECH",
            values={
                'signal_strength': 35,
                'independence': 0.6,
                'pattern_quality': 0.7,
                'deviation_from_mean': -0.25,
                'pressure_ratio': 0.18
            }
        ),
        DataPoint(
            id="ITEM_004",
            category="HEALTH",
            values={
                'signal_strength': 40,
                'independence': 0.9,
                'pattern_quality': 0.85,
                'deviation_from_mean': -0.15,
                'pressure_ratio': 0.28
            }
        ),
        DataPoint(
            id="ITEM_005",
            category="FINANCE",
            values={
                'signal_strength': 50,
                'independence': 0.75,
                'pattern_quality': 0.78,
                'deviation_from_mean': -0.38,
                'volume_trend': 1.8
            }
        ),
    ]
    
    scanner.add_batch(sample_data)
    
    # Run analysis
    results = scanner.scan()
    
    # Print report
    print(scanner.generate_report())
    
    # Export
    scanner.export("analysis_results.json")
    print("\nResults exported to analysis_results.json")
