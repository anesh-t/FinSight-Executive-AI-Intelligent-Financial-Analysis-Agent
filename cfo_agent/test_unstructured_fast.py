"""
Fast Unstructured Test - 8 representative queries (one per capability type)
"""

import sys
from pathlib import Path
import time
from statistics import mean

sys.path.insert(0, str(Path(__file__).parent / 'rag_system' / '4_enhanced_capabilities'))

from enhanced_rag_agent import EnhancedRAGAgent

print("="*80)
print("FAST UNSTRUCTURED TEST - 8 QUERIES")
print("="*80)
print()

# Representative test cases - 2 per capability
test_cases = [
    # Disclosure Summarization
    ("Disclosure", "Summarize Apple's major risk factors in 2022"),
    ("Disclosure", "What are the key risks for Apple?"),
    
    # ESG & Regulatory
    ("ESG", "What are Apple's ESG commitments in 2022?"),
    ("ESG", "Summarize Apple's environmental initiatives"),
    
    # Board Briefing
    ("Board", "Create a board briefing from Apple's 2022 10-K"),
    ("Board", "Generate an executive overview for Apple"),
    
    # Financial Extraction
    ("Financial", "What was Apple's cash flow in 2022?"),
    ("Financial", "Show me Apple's revenue in 2022"),
]

print(f"Testing {len(test_cases)} queries...\n")

# Initialize agent
print("🚀 Initializing agent...")
agent = EnhancedRAGAgent(verbose=False, use_quick_mode=True)
print("✅ Ready\n")

results = []

for i, (category, query) in enumerate(test_cases, 1):
    print(f"[{i}/{len(test_cases)}] {category}: {query[:50]}...")
    
    start = time.time()
    try:
        result = agent.query(query)
        elapsed = time.time() - start
        
        success = result.success
        status = "✅" if success else "❌"
        
        print(f"  {status} {elapsed:.2f}s - {result.capability}")
        
        if not success:
            print(f"  Error: {result.answer[:100]}")
        
        results.append({
            'category': category,
            'query': query,
            'time': elapsed,
            'success': success,
            'capability': result.capability
        })
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ❌ {elapsed:.2f}s - ERROR: {str(e)[:100]}")
        results.append({
            'category': category,
            'query': query,
            'time': elapsed,
            'success': False,
            'capability': 'error'
        })
    
    print()

agent.close()

# Summary
print("="*80)
print("SUMMARY")
print("="*80)
print()

total = len(results)
successes = sum(1 for r in results if r['success'])
times = [r['time'] for r in results if r['success']]

print(f"Total: {total}")
print(f"Success: {successes}/{total} ({successes/total*100:.0f}%)")
print(f"Failed: {total - successes}")
print()

if times:
    print(f"Average Time: {mean(times):.2f}s")
    print(f"Min Time: {min(times):.2f}s")
    print(f"Max Time: {max(times):.2f}s")
    print()

# By category
categories = {}
for r in results:
    cat = r['category']
    if cat not in categories:
        categories[cat] = {'times': [], 'successes': 0, 'total': 0}
    categories[cat]['total'] += 1
    if r['success']:
        categories[cat]['successes'] += 1
        categories[cat]['times'].append(r['time'])

print("By Category:")
for cat, stats in categories.items():
    if stats['times']:
        avg = mean(stats['times'])
        print(f"  {cat}: {stats['successes']}/{stats['total']} success, {avg:.2f}s avg")
    else:
        print(f"  {cat}: {stats['successes']}/{stats['total']} success")

print()

if times and mean(times) <= 10:
    print("✅ PERFORMANCE TARGET MET: < 10s average")
elif times and mean(times) <= 12:
    print("✅ GOOD: < 12s average")
else:
    print("⚠️  NEEDS OPTIMIZATION")

print()
print("="*80)

sys.exit(0 if successes == total else 1)
