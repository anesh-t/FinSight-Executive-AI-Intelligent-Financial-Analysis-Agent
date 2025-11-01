"""
Master Agent - Orchestrates RAG and SQL agents for hybrid queries
Handles structured and unstructured data integration
"""

from .core.orchestrator import MasterOrchestrator
from .api.unified_api import UnifiedCFOAgent

__version__ = "1.0.0"

__all__ = ['MasterOrchestrator', 'UnifiedCFOAgent']
