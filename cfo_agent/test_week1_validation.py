"""
Week 1 Validation Test - Test all 4 implemented capabilities
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent / 'rag_system' / '4_enhanced_capabilities'))

from enhanced_rag_agent import EnhancedRAGAgent

print("="*80)
print("WEEK 1 VALIDATION - 4 ENHANCED CAPABILITIES")
print("="*80)
print()

# Test cases
test_cases = [
    {
        'name': 'Disclosure Summarization',
        'query': 'Summarize the major risk factors for Apple in 2022',
        'expected_capability': 'disclosure_summary',
        'expected_sections': ['EXECUTIVE OVERVIEW', 'KEY DISCLOSURES', 'DIRECT ANSWER']
    },
    {
        'name': 'ESG & Regulatory',
        'query': 'What are Apple\'s environmental and ESG commitments in 2022?',
        'expected_capability': 'esg_regulatory',
        'expected_sections': ['ENVIRONMENTAL', 'ESG', 'DIRECT ANSWER']
    },
    {
        'name': 'Board Briefing',
        'query': 'Create an executive board briefing from Apple\'s 2022 10-K',
        'expected_capability': 'board_briefing',
        'expected_sections': ['BOARD BRIEFING', 'EXECUTIVE SUMMARY', 'DIRECT ANSWER']
    },
    {
        'name': 'Financial Extraction',
        'query': 'What was Apple\'s cash flow in 2022?',
        'expected_capability': 'financial_extraction',
        'expected_sections': ['FINANCIAL METRIC', 'DIRECT ANSWER']
    }
]

# Initialize agent
print("🚀 Initializing Enhanced RAG Agent...")
agent = EnhancedRAGAgent(verbose=False)
print("✅ Agent ready\n")

results = []
total_time = 0

for i, test in enumerate(test_cases, 1):
    print(f"{'='*80}")
    print(f"TEST {i}/4: {test['name']}")
    print(f"{'='*80}")
    print(f"Query: {test['query']}")
    print()
    
    start = time.time()
    result = agent.query(test['query'])
    elapsed = time.time() - start
    total_time += elapsed
    
    # Check results
    success = result.success
    capability_match = result.capability == test['expected_capability']
    
    # Check for expected sections
    sections_found = sum(1 for section in test['expected_sections'] if section in result.answer)
    sections_total = len(test['expected_sections'])
    
    print(f"✅ Success: {success}")
    print(f"✅ Capability: {result.capability} {'✓' if capability_match else '✗ Expected: ' + test['expected_capability']}")
    print(f"✅ Confidence: {result.confidence:.2f}")
    print(f"✅ Sections: {sections_found}/{sections_total} found")
    print(f"⏱️  Time: {elapsed:.2f}s")
    print()
    
    # Show preview
    print("📄 Answer Preview (first 300 chars):")
    print("-"*80)
    preview = result.answer[:300] + "..." if len(result.answer) > 300 else result.answer
    print(preview)
    print("-"*80)
    print()
    
    results.append({
        'name': test['name'],
        'success': success,
        'capability_match': capability_match,
        'sections_found': sections_found,
        'sections_total': sections_total,
        'time': elapsed
    })

# Summary
print(f"\n{'='*80}")
print("VALIDATION SUMMARY")
print(f"{'='*80}\n")

total_tests = len(results)
successful = sum(1 for r in results if r['success'])
capability_correct = sum(1 for r in results if r['capability_match'])
avg_time = total_time / total_tests

print(f"Total Tests: {total_tests}")
print(f"Successful: {successful}/{total_tests} ({successful/total_tests*100:.0f}%)")
print(f"Capability Detection: {capability_correct}/{total_tests} ({capability_correct/total_tests*100:.0f}%)")
print(f"Average Time: {avg_time:.2f}s")
print(f"Total Time: {total_time:.2f}s")
print()

print("Detailed Results:")
for r in results:
    status = "✅" if r['success'] else "❌"
    cap_status = "✅" if r['capability_match'] else "❌"
    sections = f"{r['sections_found']}/{r['sections_total']}"
    print(f"  {status} {r['name']:<30} Capability:{cap_status} Sections:{sections} Time:{r['time']:.2f}s")

agent.close()

print(f"\n{'='*80}")
if successful == total_tests and capability_correct == total_tests:
    print("🎉 ALL TESTS PASSED - WEEK 1 COMPLETE!")
else:
    print(f"⚠️  {total_tests - successful} test(s) failed")
print(f"{'='*80}\n")

sys.exit(0 if successful == total_tests else 1)
