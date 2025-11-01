"""
Verification Script - Test Optimized CFO Assistant
Confirms that the system meets the 7-10 second target
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent / '3_generation'))
from rag_agent import RAGAgent

print("\n" + "=" * 80)
print("🚀 CFO ASSISTANT - PERFORMANCE VERIFICATION")
print("=" * 80)
print()
print("Testing optimized configuration to verify 7-10 second target...")
print()

# Test queries
test_queries = [
    {
        "query": "What are Apple's top 3 cybersecurity risks in 2022?",
        "expected_time": "6-8 seconds",
        "top_k": 3
    },
    {
        "query": "Compare Apple and Microsoft risks in 2022",
        "expected_time": "8-10 seconds",
        "top_k": 6
    }
]

# Initialize agent (uses GPT-3.5-Turbo by default now)
print("Initializing CFO Assistant (GPT-3.5-Turbo, optimized)...")
start_init = time.time()
agent = RAGAgent(verbose=False)
init_time = time.time() - start_init
print(f"✅ Initialized in {init_time:.2f}s")
print()

results = []

for i, test in enumerate(test_queries, 1):
    print("─" * 80)
    print(f"TEST {i}/{len(test_queries)}")
    print("─" * 80)
    print(f"Query: {test['query']}")
    print(f"Expected: {test['expected_time']}")
    print()
    
    start = time.time()
    result = agent.query(test['query'], top_k=test['top_k'])
    elapsed = time.time() - start
    
    # Show answer preview
    print("ANSWER PREVIEW:")
    print(result.text[:300] + "...")
    print()
    
    print("METRICS:")
    print(f"  ⏱️  Time: {elapsed:.2f}s")
    print(f"  💰 Cost: ${result.metadata['cost']:.4f}")
    print(f"  📊 Tokens: {result.metadata['tokens']}")
    
    # Check if within target
    if elapsed <= 10:
        print(f"  ✅ Within 7-10s target!")
    else:
        print(f"  ⚠️  Exceeded target by {elapsed-10:.1f}s")
    
    print()
    
    results.append({
        'query': test['query'],
        'time': elapsed,
        'cost': result.metadata['cost'],
        'tokens': result.metadata['tokens'],
        'meets_target': elapsed <= 10
    })

agent.close()

# Summary
print("=" * 80)
print("📊 VERIFICATION SUMMARY")
print("=" * 80)
print()

total_time = sum(r['time'] for r in results)
avg_time = total_time / len(results)
total_cost = sum(r['cost'] for r in results)
all_meet_target = all(r['meets_target'] for r in results)

print(f"Total queries tested: {len(results)}")
print(f"Average time per query: {avg_time:.2f}s")
print(f"Total cost: ${total_cost:.4f}")
print()

print("Individual Results:")
print("─" * 80)
print(f"{'Query':<50} {'Time':<10} {'Target':<10}")
print("─" * 80)
for r in results:
    status = "✅ Pass" if r['meets_target'] else "❌ Fail"
    query_short = r['query'][:45] + "..." if len(r['query']) > 45 else r['query']
    print(f"{query_short:<50} {r['time']:>6.2f}s   {status}")

print("─" * 80)
print()

if all_meet_target:
    print("🎉 SUCCESS! ALL QUERIES MEET THE 7-10 SECOND TARGET!")
    print()
    print("Your CFO Assistant is fully optimized and ready for production!")
    print()
    print("Configuration:")
    print("  ✅ Model: GPT-3.5-Turbo (fast & cost-effective)")
    print("  ✅ Query Routing: Rule-based (instant)")
    print("  ✅ Database: Supabase pooler (stable connection)")
    print("  ✅ Average response time: {:.1f}s".format(avg_time))
    print("  ✅ Cost per query: ${:.4f}".format(total_cost/len(results)))
else:
    print("⚠️  Some queries exceeded the target.")
    print("Consider:")
    print("  - Using fewer chunks (top_k=3)")
    print("  - Ensuring stable internet connection")
    print("  - Running again (API times can vary)")

print()
print("=" * 80)
print("For detailed optimization info, see: OPTIMIZATION_COMPLETE.md")
print("=" * 80)
print()
