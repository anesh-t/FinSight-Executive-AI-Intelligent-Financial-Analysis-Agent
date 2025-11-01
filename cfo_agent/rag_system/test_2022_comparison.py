"""
Test specific query: Compare Apple and Microsoft risks in 2022
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / '3_generation'))
from rag_agent import RAGAgent

print("\n" + "=" * 80)
print("TESTING: Apple vs Microsoft Risks in 2022")
print("=" * 80 + "\n")

# Initialize with optimized GPT-4-Turbo
agent = RAGAgent(model="gpt-4-turbo-preview", verbose=True)

query = "compare apple and microsoft risks and show most common risks for them in 2022"

print(f"📝 Query: {query}\n")

try:
    # Run query with 6 chunks (3 per company)
    result = agent.query(query, top_k=6, format_style="detailed")
    
    print("\n" + "=" * 80)
    print("GENERATED ANSWER:")
    print("=" * 80 + "\n")
    
    print(result.text)
    
    print("\n" + "─" * 80)
    print(result.sources)
    print("─" * 80)
    
    print(f"\n⏱️  Time: {result.metadata['total_latency']:.1f}s | "
          f"💰 Cost: ${result.metadata['cost']:.4f} | "
          f"📊 Tokens: {result.metadata['tokens']}")
    
    print("\n" + "=" * 80)
    print("✅ QUERY COMPLETE")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

agent.close()
print()
