"""
CFO Assistant Demo - Test with real user queries
Demonstrates the complete end-to-end system
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / '3_generation'))
from rag_agent import RAGAgent

print("\n")
print("=" * 80)
print("CFO ASSISTANT - LIVE DEMO")
print("=" * 80)
print("\n")

# Initialize agent
agent = RAGAgent(model="gpt-4", verbose=True)

print("\n")
print("#" * 80)
print("TEST QUERY 1: Apple Risk Analysis")
print("#" * 80)
print("\n")

# Query 1: Apple risks
query1 = "show apple top 10 risks in 2023"

result1 = agent.query(query1, top_k=10)
result1.display()

print("\n\n")
input("Press Enter to continue to Query 2...")
print("\n")

print("#" * 80)
print("TEST QUERY 2: Apple vs Microsoft Risk Comparison")
print("#" * 80)
print("\n")

# Query 2: Comparison
query2 = "compare apple and microsoft top 3 risks and also mention what all common risks they have"

result2 = agent.query(query2, top_k=6)
result2.display()

# Close
agent.close()

print("\n")
print("=" * 80)
print("✅ DEMO COMPLETE")
print("=" * 80)
print()
print("Your CFO Assistant is fully operational! 🎉")
print()
print("You can now:")
print("  • Query the system with any question about 10-K filings")
print("  • Get CFO-level analysis with citations")
print("  • Compare across companies and years")
print("  • Analyze risks, strategies, trends, and more")
print()
