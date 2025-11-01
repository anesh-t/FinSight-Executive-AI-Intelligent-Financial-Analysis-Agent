"""
Debug Quick Mode
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent / 'rag_system' / '4_enhanced_capabilities'))

from enhanced_rag_agent import EnhancedRAGAgent

print("Testing Quick Mode...")
print()

agent = EnhancedRAGAgent(verbose=True, use_quick_mode=True)

query = "Summarize Apple's risks in 2022"

print(f"Query: {query}\n")

start = time.time()
result = agent.query(query)
elapsed = time.time() - start

print(f"\nSuccess: {result.success}")
print(f"Time: {elapsed:.2f}s")
print(f"Capability: {result.capability}")

if result.success:
    print(f"\nAnswer length: {len(result.answer)} chars")
    print(f"\nFirst 500 chars:")
    print(result.answer[:500])
else:
    print(f"\nError: {result.answer}")

agent.close()
