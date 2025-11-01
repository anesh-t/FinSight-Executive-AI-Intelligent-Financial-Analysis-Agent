"""
Test Fixed Comparison Query
Ensures balanced retrieval from both companies
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / '3_generation'))
from rag_agent import RAGAgent

print("\n" + "=" * 80)
print("TESTING FIXED COMPARISON QUERY")
print("=" * 80 + "\n")

# Initialize
agent = RAGAgent(model="gpt-4", verbose=True)

print("\n" + "#" * 80)
print("COMPARISON: Apple vs Microsoft Risks")
print("#" * 80 + "\n")

query = "compare apple and microsoft top 3 risks and also mention what all common risks they have"

print(f"📝 Query: {query}\n")
print("This should now:")
print("  ✅ Retrieve chunks from BOTH Apple AND Microsoft")
print("  ✅ List each company's risks separately")
print("  ✅ Identify common risks shared by both")
print("  ✅ Show differences between them")
print()

try:
    # Use top_k=6 to get 3 from each company
    result = agent.query(query, top_k=6, format_style="detailed")
    
    # Display result
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
    print("✅ TEST COMPLETE")
    print("=" * 80)
    
    # Verify sources contain both companies
    sources_text = result.sources
    has_apple = 'Apple' in sources_text
    has_microsoft = 'Microsoft' in sources_text
    
    print("\n📊 VERIFICATION:")
    print(f"  {'✅' if has_apple else '❌'} Apple sources found")
    print(f"  {'✅' if has_microsoft else '❌'} Microsoft sources found")
    
    if has_apple and has_microsoft:
        print("\n🎉 SUCCESS: Answer includes both companies!")
    else:
        print("\n⚠️  WARNING: Missing data from one company")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

agent.close()
print()
