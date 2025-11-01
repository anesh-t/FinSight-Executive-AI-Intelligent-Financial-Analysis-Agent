"""
Test Enhanced RAG Capabilities - Week 1 Quick Wins
Tests: Disclosure Summarization, ESG & Regulatory, Board Briefing, Financial Extraction
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

from master_agent import UnifiedCFOAgent


def test_enhanced_capabilities():
    """Test all 4 implemented capabilities"""
    
    print("="*80)
    print("TESTING ENHANCED RAG CAPABILITIES - WEEK 1")
    print("="*80)
    print()
    
    # Initialize agent
    print("🚀 Initializing Unified CFO Agent with Enhanced Capabilities...")
    agent = UnifiedCFOAgent(verbose=False)
    print("✅ Agent initialized\n")
    
    # Test cases for each capability
    test_cases = [
        {
            'capability': 'Disclosure Summarization',
            'query': "Summarize all major risk factors for Apple in 2022",
            'expected_sections': ['EXECUTIVE OVERVIEW', 'KEY DISCLOSURES', 'CFO PERSPECTIVE']
        },
        {
            'capability': 'ESG & Regulatory',
            'query': "What are Apple's ESG and environmental commitments in 2022?",
            'expected_sections': ['ENVIRONMENTAL COMMITMENTS', 'REGULATORY RISK']
        },
        {
            'capability': 'Board Briefing',
            'query': "Create an executive board briefing from Apple's 2022 10-K",
            'expected_sections': ['BOARD BRIEFING', 'EXECUTIVE SUMMARY', 'KEY HIGHLIGHTS']
        },
        {
            'capability': 'Financial Extraction',
            'query': "What was Apple's operating cash flow in 2022?",
            'expected_sections': ['FINANCIAL METRIC', 'Current Value']
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_cases)}: {test['capability']}")
        print(f"{'='*80}\n")
        
        print(f"📝 Query: {test['query']}\n")
        print("🔄 Processing...\n")
        
        # Execute query
        result = agent.query(test['query'])
        
        # Check result
        success = result.success
        answer = result.answer
        
        print(f"✅ Success: {success}")
        print(f"📊 Intent: {result.intent}")
        print(f"⏱️  Latency: {result.latency:.2f}s")
        print(f"📚 Data Sources: {', '.join(result.data_sources)}")
        
        # Validate expected sections
        sections_found = []
        for section in test['expected_sections']:
            if section in answer:
                sections_found.append(section)
        
        print(f"\n🔍 Section Validation:")
        print(f"   Expected: {len(test['expected_sections'])} sections")
        print(f"   Found: {len(sections_found)} sections")
        
        for section in test['expected_sections']:
            status = "✅" if section in answer else "❌"
            print(f"   {status} {section}")
        
        # Show answer preview
        print(f"\n📄 Answer Preview (first 500 chars):")
        print("-"*80)
        preview = answer[:500] + "..." if len(answer) > 500 else answer
        print(preview)
        print("-"*80)
        
        # Store result
        results.append({
            'capability': test['capability'],
            'success': success,
            'sections_found': len(sections_found),
            'sections_expected': len(test['expected_sections']),
            'latency': result.latency
        })
    
    # Summary
    print(f"\n\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}\n")
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    avg_latency = sum(r['latency'] for r in results) / len(results)
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.0f}%)")
    print(f"Average Latency: {avg_latency:.2f}s")
    print()
    
    print("Results by Capability:")
    for r in results:
        status = "✅" if r['success'] else "❌"
        sections_status = f"{r['sections_found']}/{r['sections_expected']}"
        print(f"  {status} {r['capability']:<30} Sections: {sections_status}  Latency: {r['latency']:.2f}s")
    
    # Close agent
    agent.close()
    
    print(f"\n{'='*80}")
    print("TESTING COMPLETE")
    print(f"{'='*80}\n")
    
    # Return summary
    return {
        'total': total_tests,
        'successful': successful_tests,
        'success_rate': successful_tests/total_tests,
        'avg_latency': avg_latency,
        'results': results
    }


if __name__ == "__main__":
    summary = test_enhanced_capabilities()
    
    # Exit with appropriate code
    if summary['success_rate'] == 1.0:
        print("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"⚠️  {summary['total'] - summary['successful']} test(s) failed")
        sys.exit(1)
