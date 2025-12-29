"""
Thesis loader - Load and save theses from YAML files.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
import yaml

from .models import Thesis, Catalyst
from src.config import THESES_DIR

logger = logging.getLogger(__name__)


class ThesisLoader:
    """Load and save investment theses from YAML files."""
    
    def __init__(self, theses_dir: Optional[Path] = None):
        """Initialize loader with theses directory."""
        self.theses_dir = theses_dir or THESES_DIR
        self.theses_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Thesis] = {}
    
    def load_all(self, force_reload: bool = False) -> Dict[str, Thesis]:
        """Load all theses from YAML files."""
        if self._cache and not force_reload:
            return self._cache
        
        self._cache = {}
        
        # Load from individual ticker files
        for yaml_file in self.theses_dir.glob("*.yaml"):
            try:
                thesis = self._load_file(yaml_file)
                if thesis:
                    self._cache[thesis.ticker.upper()] = thesis
                    logger.debug(f"Loaded thesis: {thesis.ticker}")
            except Exception as e:
                logger.error(f"Error loading {yaml_file}: {e}")
        
        # Also try loading from a combined definitions.yaml
        combined_file = self.theses_dir / "definitions.yaml"
        if combined_file.exists():
            try:
                with open(combined_file, 'r') as f:
                    data = yaml.safe_load(f)
                if isinstance(data, list):
                    for item in data:
                        thesis = self._parse_thesis(item)
                        if thesis:
                            self._cache[thesis.ticker.upper()] = thesis
                elif isinstance(data, dict) and 'theses' in data:
                    for item in data['theses']:
                        thesis = self._parse_thesis(item)
                        if thesis:
                            self._cache[thesis.ticker.upper()] = thesis
            except Exception as e:
                logger.error(f"Error loading definitions.yaml: {e}")
        
        logger.info(f"Loaded {len(self._cache)} theses")
        return self._cache
    
    def _load_file(self, path: Path) -> Optional[Thesis]:
        """Load a single thesis from a YAML file."""
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            return self._parse_thesis(data)
        except Exception as e:
            logger.error(f"Error parsing {path}: {e}")
            return None
    
    def _parse_thesis(self, data: dict) -> Optional[Thesis]:
        """Parse thesis from dictionary."""
        if not data or not isinstance(data, dict):
            return None
        
        try:
            # Parse catalysts if present
            catalysts = []
            if 'catalysts' in data:
                for cat_data in data['catalysts']:
                    if isinstance(cat_data, dict):
                        catalysts.append(Catalyst(**cat_data))
            
            # Build thesis
            thesis_data = {**data, 'catalysts': catalysts}
            return Thesis(**thesis_data)
        except Exception as e:
            ticker = data.get('ticker', 'unknown')
            logger.error(f"Error parsing thesis for {ticker}: {e}")
            return None
    
    def get(self, ticker: str) -> Optional[Thesis]:
        """Get thesis by ticker."""
        if not self._cache:
            self.load_all()
        return self._cache.get(ticker.upper())
    
    def save(self, thesis: Thesis) -> bool:
        """Save thesis to YAML file."""
        try:
            file_path = self.theses_dir / f"{thesis.ticker.upper()}.yaml"
            
            # Convert to dict for YAML
            data = thesis.model_dump(mode='json')
            
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            # Update cache
            self._cache[thesis.ticker.upper()] = thesis
            logger.info(f"Saved thesis: {thesis.ticker}")
            return True
        except Exception as e:
            logger.error(f"Error saving thesis {thesis.ticker}: {e}")
            return False
    
    def list_tickers(self) -> List[str]:
        """Get list of all tickers with theses."""
        if not self._cache:
            self.load_all()
        return list(self._cache.keys())
    
    def get_by_conviction(self, conviction: str) -> List[Thesis]:
        """Get theses filtered by conviction level."""
        if not self._cache:
            self.load_all()
        return [t for t in self._cache.values() if t.conviction == conviction.upper()]
