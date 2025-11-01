"""
Simple test for enhanced capabilities
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / 'rag_system' / '4_enhanced_capabilities'))

from enhanced_rag_agent import EnhancedRAGAgent

print("="*80)
print("SIMPLE TEST - Enhanced RAG Agent")
print("="*80)
print()

# Initialize
agent = EnhancedRAGAgent(verbose=True)

# Test query
query = "Summarize all major risk factors for Apple in 2022"

print(f"Query: {query}\n")
print("="*80)
print()

# Execute
result = agent.query(query)

print("="*80)
print("RESULT:")
print("="*80)
print(f"Success: {result.success}")
print(f"Capability: {result.capability}")
print(f"Confidence: {result.confidence}")
print()
print("Answer:")
print(result.answer)
print()

agent.close()
