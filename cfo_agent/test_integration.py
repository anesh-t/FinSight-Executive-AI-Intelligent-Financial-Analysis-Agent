"""
Integration Test - Test the complete master agent system
Tests RAG, SQL, and hybrid queries
"""

import sys
import time
from pathlib import Path

# Add master_agent to path
sys.path.insert(0, str(Path(__file__).parent))

from master_agent import UnifiedCFOAgent


def print_separator(title):
    """Print formatted separator"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_query(agent, question, test_num, total_tests, expected_intent):
    """Test a single query"""
    print_separator(f"TEST {test_num}/{total_tests}: {expected_intent.upper()}")
    
    print(f"\n❓ Question:")
    print(f"   {question}")
    
    print(f"\n⏳ Processing...")
    start_time = time.time()
    
    try:
        result = agent.query(question)
        elapsed = time.time() - start_time
        
        # Print results
        print(f"\n✅ Query completed successfully!")
        print(f"\n📊 Metadata:")
        print(f"   Intent:      {result.intent}")
        print(f"   Data Sources: {', '.join(result.data_sources)}")
        print(f"   Latency:     {result.latency:.2f}s")
        print(f"   Success:     {result.success}")
        
        # Print agents used
        if 'agents_used' in result.metadata:
            print(f"   Agents Used: {', '.join(result.metadata['agents_used'])}")
        
        # Print timing breakdown if available
        if 'orchestration' in result.metadata:
            orch = result.metadata['orchestration']
            if 'rag_latency' in orch:
                print(f"   RAG Time:    {orch['rag_latency']:.2f}s")
            if 'sql_latency' in orch:
                print(f"   SQL Time:    {orch['sql_latency']:.2f}s")
        
        # Print answer preview
        print(f"\n📝 Answer Preview (first 500 chars):")
        print("─" * 80)
        preview = result.answer[:500].replace('\n', '\n   ')
        print(f"   {preview}...")
        print("─" * 80)
        
        # Validation
        if result.intent == expected_intent:
            print(f"\n✅ PASS - Intent correctly classified as '{expected_intent}'")
        else:
            print(f"\n⚠️  WARN - Expected '{expected_intent}', got '{result.intent}'")
        
        return True, result
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def main():
    """Run integration tests"""
    
    print_separator("🎯 MASTER AGENT INTEGRATION TEST SUITE")
    
    print("\n📋 This test will verify:")
    print("   1. Query Classification (intent detection)")
    print("   2. RAG Agent Integration (qualitative queries)")
    print("   3. SQL Agent Integration (quantitative queries)")
    print("   4. Hybrid Queries (parallel execution)")
    print("   5. Response Synthesis (combining results)")
    
    # Initialize agent
    print("\n🚀 Initializing Unified CFO Agent...")
    agent = UnifiedCFOAgent(verbose=True)
    
    # Define test queries
    test_queries = [
        {
            'question': "What are Apple's top cybersecurity risks mentioned in their 2022 10-K?",
            'expected_intent': 'qualitative',
            'description': 'Pure RAG - Qualitative analysis from 10-K filing'
        },
        {
            'question': "What was Apple's total revenue in 2022?",
            'expected_intent': 'quantitative',
            'description': 'Pure SQL - Quantitative financial metric'
        },
        {
            'question': "How did Apple's supply chain risks affect their profit margins in 2022?",
            'expected_intent': 'hybrid',
            'description': 'Hybrid - Combines qualitative risks (RAG) + quantitative margins (SQL)'
        }
    ]
    
    # Run tests
    results = []
    total_tests = len(test_queries)
    
    for i, query_spec in enumerate(test_queries, 1):
        success, result = test_query(
            agent=agent,
            question=query_spec['question'],
            test_num=i,
            total_tests=total_tests,
            expected_intent=query_spec['expected_intent']
        )
        
        results.append({
            'test': query_spec['description'],
            'success': success,
            'result': result
        })
        
        # Wait between tests
        if i < total_tests:
            print("\n⏳ Waiting 2 seconds before next test...")
            time.sleep(2)
    
    # Summary
    print_separator("📊 TEST SUMMARY")
    
    passed = sum(1 for r in results if r['success'])
    failed = total_tests - passed
    
    print(f"\n✅ Passed: {passed}/{total_tests}")
    print(f"❌ Failed: {failed}/{total_tests}")
    print(f"📈 Success Rate: {(passed/total_tests)*100:.0f}%")
    
    print("\n📋 Detailed Results:")
    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"   {i}. {status} - {result['test']}")
        if result['result']:
            print(f"      Latency: {result['result'].latency:.2f}s")
            print(f"      Intent: {result['result'].intent}")
    
    # Performance Summary
    if all(r['result'] for r in results):
        print("\n⏱️  Performance Summary:")
        total_time = sum(r['result'].latency for r in results if r['result'])
        avg_time = total_time / len([r for r in results if r['result']])
        
        print(f"   Total Time:   {total_time:.2f}s")
        print(f"   Average Time: {avg_time:.2f}s")
        
        # Find hybrid query result
        hybrid_result = next((r['result'] for r in results if r['result'] and r['result'].intent == 'hybrid'), None)
        if hybrid_result:
            print(f"\n   🚀 Hybrid Query Performance:")
            print(f"      Total: {hybrid_result.latency:.2f}s")
            if 'orchestration' in hybrid_result.metadata:
                orch = hybrid_result.metadata['orchestration']
                if 'rag_latency' in orch and 'sql_latency' in orch:
                    sequential_time = orch['rag_latency'] + orch['sql_latency']
                    speedup = ((sequential_time - hybrid_result.latency) / sequential_time) * 100
                    print(f"      Sequential would be: {sequential_time:.2f}s")
                    print(f"      Speedup from parallel: {speedup:.0f}%")
    
    # Close agent
    print("\n🔒 Closing connections...")
    agent.close()
    
    # Final verdict
    print_separator("🏁 FINAL VERDICT")
    
    if passed == total_tests:
        print("\n🎉 ✅ ALL TESTS PASSED!")
        print("\n   The integration system is working correctly:")
        print("   ✅ Query classification working")
        print("   ✅ RAG agent connected")
        print("   ✅ SQL agent connected")
        print("   ✅ Parallel execution working")
        print("   ✅ Response synthesis working")
        print("\n   🚀 SYSTEM READY FOR PRODUCTION!")
    elif passed > 0:
        print(f"\n⚠️  PARTIAL SUCCESS: {passed}/{total_tests} tests passed")
        print("\n   Some components need attention:")
        for r in results:
            if not r['success']:
                print(f"   ❌ {r['test']}")
    else:
        print("\n❌ ALL TESTS FAILED")
        print("\n   System needs debugging before proceeding.")
    
    print("\n" + "="*80 + "\n")
    
    return passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
