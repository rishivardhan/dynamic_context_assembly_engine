"""Pytest configuration and shared fixtures."""
import sys
import os

# Add backend to path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
