"""
Comprehensive Hybrid Query Test
Tests master-level CFO questions that require both qualitative and quantitative data
Verifies: proper sourcing, logical coherence, and answer quality
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from master_agent import UnifiedCFOAgent


# Master-level CFO hybrid questions
CFO_HYBRID_QUESTIONS = [
    {
        'category': 'Risk-Financial Impact',
        'question': "How did Apple's supply chain risks disclosed in their 2022 10-K affect their gross margins?",
        'expected_sources': ['10-K Item 1A (risks)', 'Financial data (margins)'],
        'validation': {
            'should_mention': ['supply chain', 'margin', 'risk', 'impact'],
            'should_have_numbers': True,
            'should_have_qualitative': True
        }
    },
    {
        'category': 'Risk-Financial Impact',
        'question': "What cybersecurity risks did Microsoft face in 2022, and how did these concerns correlate with their R&D spending?",
        'expected_sources': ['10-K Item 1A (cyber risks)', 'Financial data (R&D)'],
        'validation': {
            'should_mention': ['cybersecurity', 'cyber', 'r&d', 'spending'],
            'should_have_numbers': True,
            'should_have_qualitative': True
        }
    },
    {
        'category': 'Strategy-Performance',
        'question': "What strategic priorities did Apple highlight in their 2022 management discussion, and how did these align with their revenue growth?",
        'expected_sources': ['10-K Item 7 (strategy)', 'Financial data (revenue)'],
        'validation': {
            'should_mention': ['strategic', 'priority', 'revenue', 'growth'],
            'should_have_numbers': True,
            'should_have_qualitative': True
        }
    },
    {
        'category': 'Risk-Profitability',
        'question': "Compare the regulatory risks mentioned by Apple and Microsoft in 2022, and analyze how these might impact their respective operating margins",
        'expected_sources': ['10-K Item 1A (both companies)', 'Financial data (margins)'],
        'validation': {
            'should_mention': ['regulatory', 'risk', 'apple', 'microsoft', 'margin'],
            'should_have_numbers': True,
            'should_have_qualitative': True
        }
    },
    {
        'category': 'Operations-Financial',
        'question': "What operational challenges did Apple describe in their 2022 10-K related to manufacturing, and what was their capital expenditure that year?",
        'expected_sources': ['10-K Item 1/7 (operations)', 'Financial data (capex)'],
        'validation': {
            'should_mention': ['operational', 'manufacturing', 'capital', 'expenditure'],
            'should_have_numbers': True,
            'should_have_qualitative': True
        }
    },
    {
        'category': 'Market Risk-Performance',
        'question': "What foreign exchange risks did Apple disclose in Item 7A for 2022, and what was their actual international revenue?",
        'expected_sources': ['10-K Item 7A (FX risk)', 'Financial data (revenue)'],
        'validation': {
            'should_mention': ['foreign exchange', 'currency', 'international', 'revenue'],
            'should_have_numbers': True,
            'should_have_qualitative': True
        }
    },
    {
        'category': 'Competition-Financial',
        'question': "How did Microsoft describe competitive pressures in their 2022 10-K, and what was their market share or revenue performance?",
        'expected_sources': ['10-K Item 1/1A (competition)', 'Financial data (revenue)'],
        'validation': {
            'should_mention': ['competitive', 'competition', 'revenue', 'market'],
            'should_have_numbers': True,
            'should_have_qualitative': True
        }
    },
    {
        'category': 'Innovation-Investment',
        'question': "What innovation strategies did Apple discuss in their 2022 management discussion, and how much did they invest in R&D?",
        'expected_sources': ['10-K Item 7 (innovation)', 'Financial data (R&D)'],
        'validation': {
            'should_mention': ['innovation', 'r&d', 'research', 'development'],
            'should_have_numbers': True,
            'should_have_qualitative': True
        }
    },
    {
        'category': 'Crisis-Financial Resilience',
        'question': "How did Apple address COVID-19 related risks in 2022, and what was their cash position that year?",
        'expected_sources': ['10-K Item 1A (COVID risks)', 'Financial data (cash)'],
        'validation': {
            'should_mention': ['covid', 'pandemic', 'cash', 'position'],
            'should_have_numbers': True,
            'should_have_qualitative': True
        }
    },
    {
        'category': 'ESG-Financial',
        'question': "What climate-related risks did Microsoft disclose in 2022, and what was their total operating expenses that year?",
        'expected_sources': ['10-K Item 1A (climate)', 'Financial data (opex)'],
        'validation': {
            'should_mention': ['climate', 'environmental', 'operating', 'expense'],
            'should_have_numbers': True,
            'should_have_qualitative': True
        }
    }
]


def print_separator(title, char="="):
    """Print formatted separator"""
    print(f"\n{char*100}")
    print(f"  {title}")
    print(f"{char*100}")


def validate_answer(answer_text, validation_criteria):
    """
    Validate answer quality and completeness
    
    Returns: dict with validation results
    """
    results = {
        'has_all_keywords': True,
        'has_numbers': False,
        'has_qualitative': False,
        'has_sources': False,
        'score': 0,
        'issues': []
    }
    
    answer_lower = answer_text.lower()
    
    # Check for required keywords
    missing_keywords = []
    for keyword in validation_criteria['should_mention']:
        if keyword.lower() not in answer_lower:
            missing_keywords.append(keyword)
    
    if missing_keywords:
        results['has_all_keywords'] = False
        results['issues'].append(f"Missing keywords: {', '.join(missing_keywords)}")
    else:
        results['score'] += 30
    
    # Check for numbers (financial data)
    import re
    if validation_criteria['should_have_numbers']:
        # Look for dollar amounts, percentages, or large numbers
        has_dollars = bool(re.search(r'\$[\d,]+\.?\d*[BMK]?', answer_text))
        has_percentages = bool(re.search(r'\d+\.?\d*%', answer_text))
        has_numbers = bool(re.search(r'\d{1,3}(,\d{3})+', answer_text))
        
        if has_dollars or has_percentages or has_numbers:
            results['has_numbers'] = True
            results['score'] += 30
        else:
            results['issues'].append("No financial numbers found")
    
    # Check for qualitative content
    if validation_criteria['should_have_qualitative']:
        qualitative_indicators = ['risk', 'strategy', 'management', 'disclosed', 'described', 
                                 'highlighted', 'discussed', 'mentioned', 'emphasized']
        qual_count = sum(1 for indicator in qualitative_indicators if indicator in answer_lower)
        
        if qual_count >= 3:
            results['has_qualitative'] = True
            results['score'] += 20
        else:
            results['issues'].append("Insufficient qualitative analysis")
    
    # Check for source citations
    has_10k_source = '10-k' in answer_lower or 'sec' in answer_lower or 'filing' in answer_lower
    has_data_source = 'financial' in answer_lower or 'database' in answer_lower or 'metric' in answer_lower
    
    if has_10k_source and has_data_source:
        results['has_sources'] = True
        results['score'] += 20
    else:
        if not has_10k_source:
            results['issues'].append("No 10-K source mentioned")
        if not has_data_source:
            results['issues'].append("No financial data source mentioned")
    
    return results


def test_hybrid_query(agent, test_spec, test_num, total_tests):
    """Test a single hybrid query with comprehensive validation"""
    
    print_separator(f"TEST {test_num}/{total_tests}: {test_spec['category']}", "=")
    
    print(f"\n📝 Question:")
    print(f"   {test_spec['question']}")
    
    print(f"\n🎯 Expected Sources:")
    for source in test_spec['expected_sources']:
        print(f"   • {source}")
    
    print(f"\n⏳ Processing query...")
    
    try:
        start_time = time.time()
        result = agent.query(test_spec['question'])
        elapsed = time.time() - start_time
        
        print(f"\n✅ Query completed in {elapsed:.2f}s")
        
        # Print metadata
        print(f"\n📊 Query Metadata:")
        print(f"   Intent:       {result.intent}")
        print(f"   Data Sources: {', '.join(result.data_sources)}")
        print(f"   Agents Used:  {', '.join(result.metadata.get('agents_used', []))}")
        
        # Show timing breakdown
        if 'orchestration' in result.metadata:
            orch = result.metadata['orchestration']
            if 'rag_latency' in orch:
                print(f"   RAG Time:     {orch['rag_latency']:.2f}s")
            if 'sql_latency' in orch:
                print(f"   SQL Time:     {orch['sql_latency']:.2f}s")
        
        # Validate answer
        print(f"\n🔍 Validating Answer Quality...")
        validation = validate_answer(result.answer, test_spec['validation'])
        
        print(f"\n📈 Validation Score: {validation['score']}/100")
        print(f"   ✓ Has all keywords:   {'✅' if validation['has_all_keywords'] else '❌'}")
        print(f"   ✓ Has numbers:        {'✅' if validation['has_numbers'] else '❌'}")
        print(f"   ✓ Has qualitative:    {'✅' if validation['has_qualitative'] else '❌'}")
        print(f"   ✓ Has sources:        {'✅' if validation['has_sources'] else '❌'}")
        
        if validation['issues']:
            print(f"\n⚠️  Issues Found:")
            for issue in validation['issues']:
                print(f"   • {issue}")
        
        # Print full answer
        print(f"\n" + "─"*100)
        print(f"📄 FULL ANSWER:")
        print("─"*100)
        print(result.answer)
        print("─"*100)
        
        # Manual review prompt
        print(f"\n🤔 Manual Review:")
        print(f"   1. Does the answer combine both qualitative (10-K) and quantitative (financial) data?")
        print(f"   2. Is the analysis logical and coherent?")
        print(f"   3. Are the sources properly attributed?")
        print(f"   4. Would this answer be useful to a CFO?")
        
        return {
            'success': True,
            'result': result,
            'validation': validation,
            'elapsed': elapsed
        }
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'success': False,
            'error': str(e),
            'validation': {'score': 0},
            'elapsed': 0
        }


def main():
    """Run comprehensive hybrid query test"""
    
    print_separator("🎯 COMPREHENSIVE HYBRID QUERY TEST", "=")
    
    print(f"\n📋 Test Overview:")
    print(f"   Total Questions: {len(CFO_HYBRID_QUESTIONS)}")
    print(f"   Categories:")
    categories = set(q['category'] for q in CFO_HYBRID_QUESTIONS)
    for cat in categories:
        count = sum(1 for q in CFO_HYBRID_QUESTIONS if q['category'] == cat)
        print(f"   • {cat}: {count} question(s)")
    
    print(f"\n🎯 This test will verify:")
    print(f"   1. Both RAG and SQL agents are invoked for hybrid queries")
    print(f"   2. Answers contain both qualitative insights and quantitative data")
    print(f"   3. Sources are properly attributed (10-K + Financial DB)")
    print(f"   4. Answers are logically coherent and make sense")
    print(f"   5. Answers would be useful to a master-level CFO")
    
    input(f"\n⏸  Press Enter to start testing...")
    
    # Initialize agent
    print(f"\n🚀 Initializing Unified CFO Agent...")
    agent = UnifiedCFOAgent(verbose=False)
    
    # Run tests
    results = []
    total_tests = len(CFO_HYBRID_QUESTIONS)
    
    for i, test_spec in enumerate(CFO_HYBRID_QUESTIONS, 1):
        result = test_hybrid_query(agent, test_spec, i, total_tests)
        results.append(result)
        
        # Pause between tests
        if i < total_tests:
            print(f"\n⏸  Test {i} complete. Press Enter to continue to next test...")
            input()
    
    # Summary
    print_separator("📊 COMPREHENSIVE TEST SUMMARY", "=")
    
    successful = sum(1 for r in results if r['success'])
    failed = total_tests - successful
    
    print(f"\n✅ Successful Queries: {successful}/{total_tests}")
    print(f"❌ Failed Queries: {failed}/{total_tests}")
    
    # Validation scores
    avg_score = sum(r['validation']['score'] for r in results if r['success']) / max(successful, 1)
    print(f"\n📈 Average Validation Score: {avg_score:.1f}/100")
    
    # Score breakdown
    score_categories = {
        'Excellent (80-100)': sum(1 for r in results if r['success'] and r['validation']['score'] >= 80),
        'Good (60-79)': sum(1 for r in results if r['success'] and 60 <= r['validation']['score'] < 80),
        'Fair (40-59)': sum(1 for r in results if r['success'] and 40 <= r['validation']['score'] < 60),
        'Poor (<40)': sum(1 for r in results if r['success'] and r['validation']['score'] < 40)
    }
    
    print(f"\n📊 Score Distribution:")
    for category, count in score_categories.items():
        print(f"   {category}: {count} queries")
    
    # Detailed results
    print(f"\n📋 Detailed Results by Category:")
    for category in set(q['category'] for q in CFO_HYBRID_QUESTIONS):
        cat_results = [
            (i, r) for i, r in enumerate(results) 
            if CFO_HYBRID_QUESTIONS[i]['category'] == category
        ]
        
        print(f"\n   {category}:")
        for idx, result in cat_results:
            status = "✅" if result['success'] else "❌"
            score = result['validation']['score'] if result['success'] else 0
            print(f"      {status} Test {idx+1}: Score {score}/100")
    
    # Performance metrics
    if successful > 0:
        avg_time = sum(r['elapsed'] for r in results if r['success']) / successful
        print(f"\n⏱️  Performance Metrics:")
        print(f"   Average Query Time: {avg_time:.2f}s")
        print(f"   Total Test Time: {sum(r['elapsed'] for r in results if r['success']):.2f}s")
    
    # Close agent
    print(f"\n🔒 Closing agent...")
    agent.close()
    
    # Final assessment
    print_separator("🏁 FINAL ASSESSMENT", "=")
    
    if avg_score >= 80:
        print(f"\n🎉 EXCELLENT! Hybrid queries are working very well!")
        print(f"   ✅ Answers are comprehensive and well-sourced")
        print(f"   ✅ Both qualitative and quantitative data present")
        print(f"   ✅ Ready for production use")
    elif avg_score >= 60:
        print(f"\n👍 GOOD! Hybrid queries are working well with minor improvements needed")
        print(f"   ✅ Core functionality working")
        print(f"   ⚠️  Some areas for enhancement")
    elif avg_score >= 40:
        print(f"\n⚠️  FAIR. Hybrid queries need improvement")
        print(f"   ⚠️  Missing some qualitative or quantitative elements")
        print(f"   ⚠️  Consider reviewing synthesis logic")
    else:
        print(f"\n❌ NEEDS WORK. Hybrid queries require significant improvement")
        print(f"   ❌ Core issues with integration or synthesis")
    
    print(f"\n" + "="*100 + "\n")
    
    return avg_score >= 60


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
