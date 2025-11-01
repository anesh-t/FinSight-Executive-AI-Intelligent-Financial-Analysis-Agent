"""
Comprehensive Test Suite - All Possible Unstructured Questions
Tests all 4 capabilities with multiple query variations
"""

import sys
from pathlib import Path
import time
from statistics import mean, median

sys.path.insert(0, str(Path(__file__).parent / 'rag_system' / '4_enhanced_capabilities'))

from enhanced_rag_agent import EnhancedRAGAgent

print("="*80)
print("COMPREHENSIVE UNSTRUCTURED QUERY TEST SUITE")
print("="*80)
print()

# Comprehensive test cases covering all possible question types
test_cases = [
    # ============================================================================
    # DISCLOSURE SUMMARIZATION (10 variations)
    # ============================================================================
    {
        'category': 'Disclosure Summarization',
        'queries': [
            "Summarize all major risk factors for Apple in 2022",
            "What are the key risks disclosed by Microsoft in 2022?",
            "List all material risks for Apple",
            "Give me an overview of Apple's risk factors",
            "What are the main business risks for Apple in 2022?",
            "Summarize Item 1A risk factors for Apple",
            "What risks does Apple face in 2022?",
            "Show me Apple's major disclosed risks",
            "What are the critical risk factors for Apple?",
            "Summarize all risks mentioned in Apple's 10-K"
        ]
    },
    
    # ============================================================================
    # ESG & REGULATORY (10 variations)
    # ============================================================================
    {
        'category': 'ESG & Regulatory',
        'queries': [
            "What are Apple's ESG commitments in 2022?",
            "Summarize Apple's environmental initiatives",
            "What are Apple's sustainability commitments?",
            "Show me Apple's climate change initiatives",
            "What regulatory risks does Apple face?",
            "Summarize Apple's ESG and environmental disclosures",
            "What are Apple's carbon reduction goals?",
            "Tell me about Apple's environmental commitments",
            "What are the regulatory challenges for Apple?",
            "Summarize Apple's ESG reporting in 2022"
        ]
    },
    
    # ============================================================================
    # BOARD BRIEFING (10 variations)
    # ============================================================================
    {
        'category': 'Board Briefing',
        'queries': [
            "Create a board briefing from Apple's 2022 10-K",
            "Generate an executive overview for Apple",
            "Prepare a board presentation from Apple's filing",
            "Create an executive summary for the board",
            "Summarize key points for board meeting - Apple 2022",
            "Give me board-level highlights from Apple's 10-K",
            "Create an executive briefing for Apple",
            "Prepare board materials from Apple's 10-K",
            "Generate a board deck from Apple's filing",
            "Create executive overview for Apple 2022"
        ]
    },
    
    # ============================================================================
    # FINANCIAL EXTRACTION (10 variations)
    # ============================================================================
    {
        'category': 'Financial Extraction',
        'queries': [
            "What was Apple's operating cash flow in 2022?",
            "Show me Apple's cash flow in 2022",
            "What was Apple's revenue in 2022?",
            "Extract Apple's R&D expense for 2022",
            "What was Apple's net income in 2022?",
            "Show me Apple's capital expenditure in 2022",
            "What was Apple's free cash flow in 2022?",
            "Extract Apple's gross profit for 2022",
            "What was Apple's operating income in 2022?",
            "Show me Apple's total revenue for 2022"
        ]
    },
    
    # ============================================================================
    # GENERAL ANALYSIS (5 variations)
    # ============================================================================
    {
        'category': 'General Analysis',
        'queries': [
            "Tell me about Apple's business in 2022",
            "What does Apple do?",
            "Summarize Apple's operations",
            "What are Apple's main products?",
            "Describe Apple's business model"
        ]
    }
]

# Initialize agent
print("🚀 Initializing Enhanced RAG Agent (Quick Mode)...")
agent = EnhancedRAGAgent(verbose=False, use_quick_mode=True)
print("✅ Agent ready\n")

# Track results
all_results = []
category_results = {}

total_queries = sum(len(cat['queries']) for cat in test_cases)
current_query = 0

print(f"Testing {total_queries} queries across {len(test_cases)} categories...\n")

# Test each category
for category_data in test_cases:
    category = category_data['category']
    queries = category_data['queries']
    
    print(f"\n{'='*80}")
    print(f"CATEGORY: {category} ({len(queries)} queries)")
    print(f"{'='*80}\n")
    
    category_times = []
    category_successes = 0
    
    for i, query in enumerate(queries, 1):
        current_query += 1
        
        print(f"[{current_query}/{total_queries}] Testing: {query[:60]}...")
        
        start = time.time()
        result = agent.query(query)
        elapsed = time.time() - start
        
        success = result.success
        category_times.append(elapsed)
        if success:
            category_successes += 1
        
        status = "✅" if success else "❌"
        print(f"  {status} {elapsed:.2f}s - {result.capability}")
        
        all_results.append({
            'category': category,
            'query': query,
            'time': elapsed,
            'success': success,
            'capability': result.capability,
            'confidence': result.confidence
        })
    
    # Category summary
    avg_time = mean(category_times)
    median_time = median(category_times)
    min_time = min(category_times)
    max_time = max(category_times)
    
    category_results[category] = {
        'total': len(queries),
        'successes': category_successes,
        'avg_time': avg_time,
        'median_time': median_time,
        'min_time': min_time,
        'max_time': max_time,
        'times': category_times
    }
    
    print(f"\n  Category Summary:")
    print(f"    Success Rate: {category_successes}/{len(queries)} ({category_successes/len(queries)*100:.0f}%)")
    print(f"    Avg Time: {avg_time:.2f}s")
    print(f"    Median Time: {median_time:.2f}s")
    print(f"    Range: {min_time:.2f}s - {max_time:.2f}s")

agent.close()

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print(f"\n\n{'='*80}")
print("COMPREHENSIVE TEST SUMMARY")
print(f"{'='*80}\n")

total_tests = len(all_results)
total_successes = sum(1 for r in all_results if r['success'])
all_times = [r['time'] for r in all_results]

print(f"Total Queries Tested: {total_tests}")
print(f"Successful: {total_successes}/{total_tests} ({total_successes/total_tests*100:.1f}%)")
print(f"Failed: {total_tests - total_successes}")
print()

print("Performance Metrics:")
print(f"  Average Time: {mean(all_times):.2f}s")
print(f"  Median Time: {median(all_times):.2f}s")
print(f"  Min Time: {min(all_times):.2f}s")
print(f"  Max Time: {max(all_times):.2f}s")
print()

# Performance by category
print("Performance by Category:")
print("-" * 80)
for category, stats in category_results.items():
    success_rate = stats['successes'] / stats['total'] * 100
    print(f"\n{category}:")
    print(f"  Success Rate: {stats['successes']}/{stats['total']} ({success_rate:.0f}%)")
    print(f"  Avg Time: {stats['avg_time']:.2f}s")
    print(f"  Median Time: {stats['median_time']:.2f}s")
    print(f"  Range: {stats['min_time']:.2f}s - {stats['max_time']:.2f}s")

# Speed analysis
print(f"\n{'='*80}")
print("SPEED ANALYSIS")
print(f"{'='*80}\n")

fast_queries = sum(1 for t in all_times if t < 8)
medium_queries = sum(1 for t in all_times if 8 <= t < 12)
slow_queries = sum(1 for t in all_times if t >= 12)

print(f"Fast (< 8s):     {fast_queries} queries ({fast_queries/total_tests*100:.1f}%)")
print(f"Medium (8-12s):  {medium_queries} queries ({medium_queries/total_tests*100:.1f}%)")
print(f"Slow (>= 12s):   {slow_queries} queries ({slow_queries/total_tests*100:.1f}%)")
print()

# Target achievement
target_time = 10.0
queries_meeting_target = sum(1 for t in all_times if t <= target_time)
print(f"Queries Meeting Target (<= {target_time}s): {queries_meeting_target}/{total_tests} ({queries_meeting_target/total_tests*100:.1f}%)")
print()

# Recommendations
print(f"{'='*80}")
print("RECOMMENDATIONS")
print(f"{'='*80}\n")

if mean(all_times) <= 10:
    print("✅ EXCELLENT: Average time is under 10 seconds!")
elif mean(all_times) <= 12:
    print("✅ GOOD: Average time is under 12 seconds")
else:
    print("⚠️  NEEDS OPTIMIZATION: Average time exceeds 12 seconds")

print()

if queries_meeting_target / total_tests >= 0.8:
    print("✅ 80%+ queries meet target - Performance is good!")
elif queries_meeting_target / total_tests >= 0.6:
    print("⚠️  60-80% queries meet target - Some optimization needed")
else:
    print("❌ < 60% queries meet target - Significant optimization needed")

print()

# Identify slowest queries
print("Slowest 5 Queries:")
slowest = sorted(all_results, key=lambda x: x['time'], reverse=True)[:5]
for i, r in enumerate(slowest, 1):
    print(f"  {i}. {r['time']:.2f}s - {r['query'][:60]}...")
    print(f"     Category: {r['category']}, Capability: {r['capability']}")

print()

# Identify fastest queries
print("Fastest 5 Queries:")
fastest = sorted(all_results, key=lambda x: x['time'])[:5]
for i, r in enumerate(fastest, 1):
    print(f"  {i}. {r['time']:.2f}s - {r['query'][:60]}...")
    print(f"     Category: {r['category']}, Capability: {r['capability']}")

print(f"\n{'='*80}")
print("TEST COMPLETE")
print(f"{'='*80}\n")

# Exit code
if total_successes == total_tests and mean(all_times) <= 12:
    print("🎉 ALL TESTS PASSED WITH GOOD PERFORMANCE!")
    sys.exit(0)
elif total_successes == total_tests:
    print("✅ ALL TESTS PASSED (Performance could be improved)")
    sys.exit(0)
else:
    print(f"⚠️  {total_tests - total_successes} test(s) failed")
    sys.exit(1)
