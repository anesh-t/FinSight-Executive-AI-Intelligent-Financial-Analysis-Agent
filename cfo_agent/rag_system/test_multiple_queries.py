"""
Test Multiple Query Types - Comprehensive Testing
Tests different query types and provides summaries
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / '3_generation'))
from rag_agent import RAGAgent

# Test queries
TEST_QUERIES = [
    {
        "name": "Risk Analysis",
        "query": "What are Apple's top 5 cybersecurity risks in 2023?",
        "top_k": 5
    },
    {
        "name": "Comparison",
        "query": "Compare Microsoft and Google AI strategies",
        "top_k": 6
    },
    {
        "name": "Trend Analysis",
        "query": "What are the emerging regulatory risks across tech companies?",
        "top_k": 8
    },
    {
        "name": "Strategic Explanation",
        "query": "Explain Meta's metaverse strategy and financial implications",
        "top_k": 5
    },
    {
        "name": "Financial Focus",
        "query": "What supply chain challenges affected Apple and their financial impact?",
        "top_k": 5
    }
]

print("\n" + "=" * 80)
print("COMPREHENSIVE QUERY TESTING")
print("=" * 80 + "\n")

# Initialize agent
agent = RAGAgent(model="gpt-4", verbose=False)  # verbose=False for cleaner output

results_summary = []

for i, test in enumerate(TEST_QUERIES, 1):
    print(f"\n{'#' * 80}")
    print(f"TEST {i}/{len(TEST_QUERIES)}: {test['name']}")
    print(f"{'#' * 80}")
    print(f"\n📝 Query: {test['query']}\n")
    
    try:
        # Run query
        result = agent.query(test['query'], top_k=test['top_k'], format_style="compact")
        
        # Show abbreviated answer (first 800 chars)
        print("─" * 80)
        print("ANSWER (Preview):")
        print("─" * 80)
        answer_preview = result.text[:800] + "..." if len(result.text) > 800 else result.text
        print(answer_preview)
        print()
        
        # Show summary stats
        print("─" * 80)
        print("STATISTICS:")
        print("─" * 80)
        print(f"✅ Answer generated successfully")
        print(f"📊 Tokens: {result.metadata['tokens']}")
        print(f"💰 Cost: ${result.metadata['cost']:.4f}")
        print(f"⏱️  Time: {result.metadata['total_latency']:.1f}s")
        print(f"📚 Sources: {result.metadata['source_count']} documents")
        print(f"🔍 Chunks: {result.metadata['retrieval_chunks']} retrieved")
        
        # Store summary
        results_summary.append({
            'test': test['name'],
            'query': test['query'],
            'success': True,
            'tokens': result.metadata['tokens'],
            'cost': result.metadata['cost'],
            'time': result.metadata['total_latency'],
            'sources': result.metadata['source_count'],
            'answer_length': len(result.text)
        })
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        results_summary.append({
            'test': test['name'],
            'query': test['query'],
            'success': False,
            'error': str(e)
        })
    
    print()

# Final summary
print("\n" + "=" * 80)
print("COMPREHENSIVE TEST SUMMARY")
print("=" * 80 + "\n")

successful = sum(1 for r in results_summary if r['success'])
failed = len(results_summary) - successful

print(f"📊 Overall Results: {successful}/{len(results_summary)} queries successful\n")

if successful > 0:
    print("─" * 80)
    print("SUCCESSFUL QUERIES:")
    print("─" * 80)
    
    total_tokens = 0
    total_cost = 0
    total_time = 0
    
    for r in results_summary:
        if r['success']:
            print(f"\n✅ {r['test']}")
            print(f"   Query: {r['query'][:60]}...")
            print(f"   Tokens: {r['tokens']} | Cost: ${r['cost']:.4f} | Time: {r['time']:.1f}s")
            print(f"   Answer: {r['answer_length']} chars | Sources: {r['sources']}")
            
            total_tokens += r['tokens']
            total_cost += r['cost']
            total_time += r['time']
    
    print("\n" + "─" * 80)
    print("AGGREGATE STATISTICS:")
    print("─" * 80)
    print(f"Total Tokens:    {total_tokens:,}")
    print(f"Total Cost:      ${total_cost:.4f}")
    print(f"Total Time:      {total_time:.1f}s")
    print(f"Avg per Query:   {total_tokens//successful} tokens, ${total_cost/successful:.4f}, {total_time/successful:.1f}s")

if failed > 0:
    print("\n" + "─" * 80)
    print("FAILED QUERIES:")
    print("─" * 80)
    for r in results_summary:
        if not r['success']:
            print(f"\n❌ {r['test']}")
            print(f"   Query: {r['query']}")
            print(f"   Error: {r['error']}")

print("\n" + "=" * 80)
print("✅ TESTING COMPLETE")
print("=" * 80)
print()

# Close agent
agent.close()

# Print final verdict
print("🎯 VERDICT:")
if successful == len(results_summary):
    print("   ✅ ALL TESTS PASSED - System is fully operational!")
    print("   🚀 Ready for production use!")
elif successful > len(results_summary) // 2:
    print(f"   ⚠️  MOSTLY WORKING - {successful}/{len(results_summary)} tests passed")
    print("   🔧 Some queries need attention")
else:
    print(f"   ❌ ISSUES DETECTED - Only {successful}/{len(results_summary)} tests passed")
    print("   🔍 Review errors above")

print()
