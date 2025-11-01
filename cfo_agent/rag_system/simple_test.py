"""
Simple 3-Query Test - Fast with immediate output
"""

import sys
from pathlib import Path

print("=" * 80)
print("STARTING CFO ASSISTANT TEST")
print("=" * 80)
print()

sys.path.insert(0, str(Path(__file__).parent / '3_generation'))

print("Importing modules...")
from rag_agent import RAGAgent
print("✅ Imports successful")
print()

print("Initializing CFO Assistant...")
agent = RAGAgent(model="gpt-4", verbose=False)
print("✅ Agent initialized")
print()

# Test 3 queries
queries = [
    ("Risk Analysis", "What are Apple's main cybersecurity risks?", 3),
    ("Comparison", "Compare Google and Microsoft cloud strategies", 4),
    ("Strategy", "Explain Meta's AI strategy", 3)
]

results = []

for i, (name, query, top_k) in enumerate(queries, 1):
    print(f"\n{'#' * 80}")
    print(f"QUERY {i}/3: {name}")
    print(f"{'#' * 80}")
    print(f"Question: {query}")
    print(f"Retrieving {top_k} chunks...")
    print()
    
    try:
        result = agent.query(query, top_k=top_k, format_style="compact")
        
        # Show first 500 chars of answer
        print("ANSWER PREVIEW:")
        print("-" * 80)
        preview = result.text[:500] + "..." if len(result.text) > 500 else result.text
        print(preview)
        print()
        
        print("STATS:")
        print(f"  ✅ Success")
        print(f"  📊 {result.metadata['tokens']} tokens")
        print(f"  💰 ${result.metadata['cost']:.4f}")
        print(f"  ⏱️  {result.metadata['total_latency']:.1f}s")
        print(f"  📚 {result.metadata['source_count']} sources")
        
        results.append({
            'name': name,
            'success': True,
            'tokens': result.metadata['tokens'],
            'cost': result.metadata['cost'],
            'time': result.metadata['total_latency']
        })
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results.append({'name': name, 'success': False, 'error': str(e)})

agent.close()

# Summary
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

successful = sum(1 for r in results if r['success'])
print(f"\n✅ {successful}/3 queries successful\n")

if successful > 0:
    total_cost = sum(r['cost'] for r in results if r['success'])
    total_time = sum(r['time'] for r in results if r['success'])
    total_tokens = sum(r['tokens'] for r in results if r['success'])
    
    print(f"Total Tokens: {total_tokens:,}")
    print(f"Total Cost: ${total_cost:.4f}")
    print(f"Total Time: {total_time:.1f}s")
    print(f"Avg/Query: ${total_cost/successful:.4f}, {total_time/successful:.1f}s")

print("\n" + "=" * 80)
if successful == 3:
    print("🎉 ALL TESTS PASSED - SYSTEM FULLY OPERATIONAL!")
else:
    print(f"⚠️  {successful}/3 tests passed")
print("=" * 80)
print()
