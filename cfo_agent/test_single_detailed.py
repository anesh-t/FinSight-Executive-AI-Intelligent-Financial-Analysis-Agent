"""Show one complete answer for manual review"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from master_agent import UnifiedCFOAgent

agent = UnifiedCFOAgent(verbose=False)

print("\n" + "="*100)
print("📋 COMPLETE ANSWER REVIEW")
print("="*100)

question = "What were Apple's main supply chain risks in 2022, and what was their gross margin?"

print(f"\n📝 Question: {question}\n")
print("⏳ Processing...\n")

result = agent.query(question)

print("="*100)
print("✅ COMPLETE ANSWER:")
print("="*100)
print(result.answer)
print("="*100)

print(f"\n📊 Metadata:")
print(f"   Intent: {result.intent}")
print(f"   Sources: {result.data_sources}")
print(f"   Success: {result.success}")
print(f"   Latency: {result.latency:.2f}s")

agent.close()

print("\n" + "="*100)
print("🔍 MANUAL REVIEW CHECKLIST:")
print("="*100)
print("""
1. ✓ Does the answer include supply chain risks from 10-K?
2. ✓ Does the answer include gross margin percentage?
3. ✓ Are the risks relevant and detailed?
4. ✓ Is the gross margin number correct (~43% for Apple 2022)?
5. ✓ Does the combined answer make logical sense?
6. ✓ Are sources properly cited?
7. ✓ Would this be useful to a CFO?
""")
print("="*100 + "\n")
