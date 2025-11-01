"""Final validation with 3 diverse hybrid queries"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from master_agent import UnifiedCFOAgent
import time

def test_query(agent, question, test_num):
    """Test a single hybrid query"""
    print(f"\n{'='*100}")
    print(f"TEST {test_num}: HYBRID QUERY")
    print(f"{'='*100}")
    print(f"\nQuestion: {question}\n")
    
    start = time.time()
    result = agent.query(question)
    elapsed = time.time() - start
    
    print(f"\n{'─'*100}")
    print(f"RESULT:")
    print(f"{'─'*100}")
    print(f"✅ Success: {result.success}")
    print(f"⏱️  Time: {elapsed:.2f}s")
    print(f"🎯 Intent: {result.intent}")
    print(f"📚 Sources: {', '.join(result.data_sources)}")
    
    # Validation
    has_qualitative = 'risk' in result.answer.lower() or 'strategy' in result.answer.lower() or 'disclosed' in result.answer.lower()
    has_quantitative = '$' in result.answer or '%' in result.answer or any(word in result.answer.lower() for word in ['million', 'billion'])
    
    print(f"\n📊 Validation:")
    print(f"   Qualitative content: {'✅' if has_qualitative else '❌'}")
    print(f"   Quantitative data: {'✅' if has_quantitative else '❌'}")
    
    # Show first 800 chars
    print(f"\n📄 Answer Preview:")
    print(f"{'─'*100}")
    preview = result.answer[:800]
    print(preview + "...")
    print(f"{'─'*100}")
    
    return {
        'success': result.success,
        'time': elapsed,
        'has_both': has_qualitative and has_quantitative
    }


# Main test
print("\n" + "="*100)
print("🎯 FINAL HYBRID QUERY VALIDATION")
print("="*100)
print("\nTesting 3 diverse CFO-level hybrid questions...")

agent = UnifiedCFOAgent(verbose=False)

queries = [
    "What cybersecurity risks did Microsoft face in 2022, and what was their R&D spending?",
    "How did Apple's innovation strategies in 2022 align with their revenue performance?",
    "What regulatory risks did Apple disclose in 2022, and what was their operating margin?"
]

results = []
for i, q in enumerate(queries, 1):
    result = test_query(agent, q, i)
    results.append(result)
    if i < len(queries):
        print(f"\n⏳ Waiting 3 seconds...")
        time.sleep(3)

agent.close()

# Summary
print(f"\n{'='*100}")
print(f"📊 FINAL SUMMARY")
print(f"{'='*100}")

successful = sum(1 for r in results if r['success'])
has_both = sum(1 for r in results if r['has_both'])
avg_time = sum(r['time'] for r in results) / len(results)

print(f"\n✅ Success Rate: {successful}/{len(results)} ({successful/len(results)*100:.0f}%)")
print(f"📊 Has Both Sources: {has_both}/{len(results)} ({has_both/len(results)*100:.0f}%)")
print(f"⏱️  Average Time: {avg_time:.2f}s")

if successful == len(results) and has_both == len(results):
    print(f"\n🎉 ✅ ALL TESTS PASSED!")
    print(f"\n   Hybrid query system is WORKING PERFECTLY:")
    print(f"   ✅ All queries successful")
    print(f"   ✅ All combine qualitative + quantitative data")
    print(f"   ✅ Average response time: {avg_time:.1f}s")
    print(f"   ✅ Ready for production!")
else:
    print(f"\n⚠️  Some issues detected")

print(f"\n{'='*100}\n")
