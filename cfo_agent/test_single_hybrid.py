"""Quick single hybrid query test"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from master_agent import UnifiedCFOAgent

# Test
agent = UnifiedCFOAgent(verbose=True)

question = "How did Apple's supply chain risks in 2022 affect their gross margins?"

print(f"\n{'='*100}")
print(f"HYBRID QUERY TEST")
print(f"{'='*100}")
print(f"\nQuestion: {question}\n")

result = agent.query(question)

print(f"\n{'='*100}")
print(f"RESULT")
print(f"{'='*100}")
print(f"Intent: {result.intent}")
print(f"Sources: {result.data_sources}")
print(f"Success: {result.success}")
print(f"Latency: {result.latency:.2f}s")
print(f"\nAnswer:\n{result.answer}")
print(f"\n{'='*100}")

agent.close()
