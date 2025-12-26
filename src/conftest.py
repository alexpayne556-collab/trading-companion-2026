"""Conftest to fix Python path for pytest."""
import sys
import os
# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
