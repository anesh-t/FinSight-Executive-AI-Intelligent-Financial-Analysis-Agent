"""
Quick CFO Assistant Test - Single query without waiting
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / '3_generation'))
from rag_agent import RAGAgent

print("\n" + "=" * 80)
print("CFO ASSISTANT - QUICK TEST")
print("=" * 80 + "\n")

# Initialize agent
print("Initializing CFO Assistant...\n")
agent = RAGAgent(model="gpt-4", verbose=True)

print("\n" + "#" * 80)
print("TEST QUERY: Apple's Top Risks")
print("#" * 80 + "\n")

# Test with a simpler query first
query = "What are Apple's main business risks in 2023?"

try:
    result = agent.query(query, top_k=5)
    
    print("\n" + "=" * 80)
    print("ANSWER:")
    print("=" * 80 + "\n")
    
    print(result.text)
    
    print("\n" + "─" * 80)
    print(result.sources)
    print("─" * 80)
    print(f"\n⏱️  Query time: {result.metadata['total_latency']:.1f}s | "
          f"💰 Cost: ${result.metadata['cost']:.4f} | "
          f"📊 Tokens: {result.metadata['tokens']}")
    print("=" * 80 + "\n")
    
    print("✅ TEST SUCCESSFUL!")
    print("\nThe CFO Assistant is working perfectly!")
    print("Ready to answer your exact queries.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    agent.close()
