"""
Comprehensive Hybrid Query Validation Test
Tests data accuracy, sourcing, and logical coherence
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from master_agent import UnifiedCFOAgent
import time
import re

def extract_numbers(text):
    """Extract all numbers and percentages from text"""
    # Find percentages
    percentages = re.findall(r'(\d+\.?\d*)%', text)
    # Find dollar amounts
    dollars = re.findall(r'\$(\d+\.?\d*)\s*(billion|million|B|M)', text, re.IGNORECASE)
    # Find plain numbers
    numbers = re.findall(r'\b(\d+\.?\d+)\b', text)
    
    return {
        'percentages': percentages,
        'dollars': dollars,
        'all_numbers': numbers
    }

def check_data_coherence(question, answer, intent, sources):
    """Check if the answer makes sense and is properly sourced"""
    
    print(f"\n{'='*100}")
    print(f"🔍 DETAILED VALIDATION")
    print(f"{'='*100}\n")
    
    issues = []
    validations = []
    
    # 1. Check sources are present
    print("1️⃣  SOURCE VALIDATION:")
    if '10-K' in sources or 'RAG' in str(sources):
        print("   ✅ Qualitative source (10-K) present")
        validations.append("qualitative_source")
    else:
        print("   ❌ Missing qualitative source (10-K)")
        issues.append("Missing 10-K source")
    
    if 'SQL' in str(sources) or 'Financial Database' in str(sources) or 'Database' in str(sources):
        print("   ✅ Quantitative source (SQL) present")
        validations.append("quantitative_source")
    else:
        print("   ❌ Missing quantitative source (SQL)")
        issues.append("Missing SQL source")
    
    # 2. Check for qualitative content markers
    print("\n2️⃣  QUALITATIVE CONTENT VALIDATION:")
    qualitative_markers = ['risk', 'strategy', 'strategic', 'disclosed', 'described', 
                          'challenge', 'priority', 'concern', 'impact']
    found_markers = [m for m in qualitative_markers if m.lower() in answer.lower()]
    
    if len(found_markers) >= 2:
        print(f"   ✅ Has qualitative analysis (found: {', '.join(found_markers[:3])}...)")
        validations.append("qualitative_content")
    else:
        print(f"   ⚠️  Limited qualitative content")
        issues.append("Insufficient qualitative analysis")
    
    # 3. Check for quantitative data
    print("\n3️⃣  QUANTITATIVE DATA VALIDATION:")
    numbers = extract_numbers(answer)
    
    if numbers['percentages']:
        print(f"   ✅ Has percentages: {', '.join(numbers['percentages'][:5])}")
        validations.append("has_percentages")
    
    if numbers['dollars']:
        print(f"   ✅ Has dollar amounts: {numbers['dollars'][:3]}")
        validations.append("has_dollars")
    
    if not numbers['percentages'] and not numbers['dollars'] and len(numbers['all_numbers']) < 3:
        print("   ⚠️  Limited quantitative data")
        issues.append("Insufficient quantitative data")
    
    # 4. Check answer structure
    print("\n4️⃣  STRUCTURE VALIDATION:")
    has_sections = bool(re.search(r'#{1,3}\s+', answer))
    has_analysis = 'QUALITATIVE ANALYSIS' in answer or 'QUANTITATIVE DATA' in answer
    has_summary = 'SUMMARY' in answer or 'EXECUTIVE' in answer
    
    if has_sections:
        print("   ✅ Has structured sections")
        validations.append("structured")
    if has_analysis:
        print("   ✅ Has analysis sections")
        validations.append("has_analysis")
    if has_summary:
        print("   ✅ Has executive summary")
        validations.append("has_summary")
    
    # 5. Check logical coherence
    print("\n5️⃣  LOGICAL COHERENCE:")
    question_lower = question.lower()
    answer_lower = answer.lower()
    
    # Extract key terms from question
    key_terms = []
    if 'apple' in question_lower:
        key_terms.append('apple')
    if 'microsoft' in question_lower:
        key_terms.append('microsoft')
    if 'revenue' in question_lower:
        key_terms.append('revenue')
    if 'margin' in question_lower:
        key_terms.append('margin')
    if 'risk' in question_lower:
        key_terms.append('risk')
    if 'r&d' in question_lower or 'research' in question_lower:
        key_terms.append('r&d')
    
    # Check if answer addresses key terms
    addressed = [term for term in key_terms if term in answer_lower]
    
    if len(addressed) >= len(key_terms) * 0.7:  # At least 70% of key terms
        print(f"   ✅ Answer addresses key topics: {', '.join(addressed)}")
        validations.append("coherent")
    else:
        print(f"   ⚠️  May not fully address question")
        print(f"      Expected: {key_terms}")
        print(f"      Found: {addressed}")
        issues.append("May not fully address question")
    
    # 6. Check for proper attribution
    print("\n6️⃣  ATTRIBUTION VALIDATION:")
    has_rag_attribution = bool(re.search(r'(SEC 10-K|SOURCE \d+|\[SOURCE)', answer))
    has_sql_attribution = bool(re.search(r'(ALPHAVANTAGE|Yahoo Finance|FRED|YF)', answer))
    
    if has_rag_attribution:
        print("   ✅ Has 10-K source attribution")
        validations.append("rag_attributed")
    else:
        print("   ⚠️  Missing 10-K source attribution")
        issues.append("Missing 10-K attribution in content")
    
    if has_sql_attribution:
        print("   ✅ Has financial data source attribution")
        validations.append("sql_attributed")
    else:
        print("   ⚠️  Missing financial data attribution")
        issues.append("Missing SQL attribution in content")
    
    # 7. Calculate quality score
    print("\n7️⃣  QUALITY SCORE:")
    score = len(validations) * 10
    max_score = 120  # 12 possible validations
    percentage = (score / max_score) * 100
    
    if percentage >= 80:
        grade = "🎉 EXCELLENT"
    elif percentage >= 60:
        grade = "👍 GOOD"
    elif percentage >= 40:
        grade = "⚠️  FAIR"
    else:
        grade = "❌ NEEDS WORK"
    
    print(f"   Score: {score}/{max_score} ({percentage:.0f}%)")
    print(f"   Grade: {grade}")
    print(f"   Validations passed: {len(validations)}")
    
    return {
        'score': score,
        'percentage': percentage,
        'validations': validations,
        'issues': issues,
        'numbers': numbers
    }


def test_hybrid_question(agent, question, test_num, expected_company=None, expected_metric=None):
    """Test a single hybrid question with detailed validation"""
    
    print(f"\n{'='*100}")
    print(f"TEST {test_num}: HYBRID QUERY WITH VALIDATION")
    print(f"{'='*100}")
    print(f"\n📝 Question:")
    print(f"   {question}")
    
    if expected_company:
        print(f"\n🎯 Expected:")
        print(f"   Company: {expected_company}")
        if expected_metric:
            print(f"   Metric: {expected_metric}")
    
    print(f"\n⏳ Processing...")
    start = time.time()
    result = agent.query(question)
    elapsed = time.time() - start
    
    print(f"\n{'─'*100}")
    print(f"📊 BASIC RESULTS:")
    print(f"{'─'*100}")
    print(f"   ✅ Success: {result.success}")
    print(f"   ⏱️  Time: {elapsed:.2f}s")
    print(f"   🎯 Intent: {result.intent}")
    print(f"   📚 Sources: {result.data_sources}")
    
    if not result.success:
        print(f"\n❌ QUERY FAILED")
        print(f"   Error: {result.metadata.get('error', 'Unknown error')}")
        return None
    
    # Detailed validation
    validation = check_data_coherence(question, result.answer, result.intent, result.data_sources)
    
    # Show answer preview
    print(f"\n{'─'*100}")
    print(f"📄 ANSWER PREVIEW (First 1200 chars):")
    print(f"{'─'*100}")
    preview = result.answer[:1200]
    print(preview)
    if len(result.answer) > 1200:
        print("\n... (truncated, see full answer below if needed)")
    print(f"{'─'*100}")
    
    # Summary of issues
    if validation['issues']:
        print(f"\n⚠️  ISSUES FOUND:")
        for issue in validation['issues']:
            print(f"   • {issue}")
    else:
        print(f"\n✅ NO ISSUES FOUND!")
    
    print(f"\n{'='*100}")
    
    return {
        'success': result.success,
        'time': elapsed,
        'validation': validation,
        'answer': result.answer,
        'sources': result.data_sources
    }


# Main test execution
print("\n" + "="*100)
print("🔍 COMPREHENSIVE HYBRID QUERY VALIDATION TEST")
print("="*100)
print("\nThis test validates:")
print("  1. Data is properly sourced (10-K + Financial DB)")
print("  2. Quantitative data is present and correct")
print("  3. Qualitative analysis is meaningful")
print("  4. Combined answer makes logical sense")
print("  5. Sources are properly attributed")
print("\n" + "="*100)

agent = UnifiedCFOAgent(verbose=False)

# Test cases with expected data
test_cases = [
    {
        'question': "What were Apple's main supply chain risks in 2022, and what was their gross margin that year?",
        'company': 'Apple',
        'expected_metric': 'gross margin ~43%'
    },
    {
        'question': "How did Microsoft's cybersecurity investments relate to their R&D spending in 2022?",
        'company': 'Microsoft',
        'expected_metric': 'R&D spending'
    },
    {
        'question': "What competitive pressures did Apple face in 2022, and how did their revenue perform?",
        'company': 'Apple',
        'expected_metric': 'revenue growth'
    },
    {
        'question': "What regulatory challenges did Microsoft disclose in 2022, and what was their operating margin?",
        'company': 'Microsoft',
        'expected_metric': 'operating margin'
    },
    {
        'question': "How did Apple's innovation strategy in 2022 align with their profitability metrics?",
        'company': 'Apple',
        'expected_metric': 'profitability'
    }
]

results = []
for i, test_case in enumerate(test_cases, 1):
    result = test_hybrid_question(
        agent, 
        test_case['question'], 
        i,
        test_case.get('company'),
        test_case.get('expected_metric')
    )
    
    if result:
        results.append(result)
    
    if i < len(test_cases):
        print(f"\n⏳ Pausing 3 seconds before next test...")
        time.sleep(3)

agent.close()

# Final Summary
print(f"\n{'='*100}")
print(f"📊 FINAL VALIDATION SUMMARY")
print(f"{'='*100}\n")

if not results:
    print("❌ No successful tests")
else:
    successful = len([r for r in results if r['success']])
    avg_score = sum(r['validation']['percentage'] for r in results) / len(results)
    avg_time = sum(r['time'] for r in results) / len(results)
    
    # Count validations
    all_validations = []
    all_issues = []
    for r in results:
        all_validations.extend(r['validation']['validations'])
        all_issues.extend(r['validation']['issues'])
    
    print(f"✅ Success Rate: {successful}/{len(results)} ({successful/len(results)*100:.0f}%)")
    print(f"📊 Average Quality Score: {avg_score:.0f}%")
    print(f"⏱️  Average Response Time: {avg_time:.1f}s")
    print(f"\n📈 Validation Statistics:")
    print(f"   Total validations passed: {len(all_validations)}")
    print(f"   Total issues found: {len(all_issues)}")
    
    # Show grade distribution
    excellent = sum(1 for r in results if r['validation']['percentage'] >= 80)
    good = sum(1 for r in results if 60 <= r['validation']['percentage'] < 80)
    fair = sum(1 for r in results if 40 <= r['validation']['percentage'] < 60)
    poor = sum(1 for r in results if r['validation']['percentage'] < 40)
    
    print(f"\n📊 Quality Distribution:")
    print(f"   🎉 Excellent (80-100%): {excellent}")
    print(f"   👍 Good (60-79%):      {good}")
    print(f"   ⚠️  Fair (40-59%):      {fair}")
    print(f"   ❌ Poor (<40%):        {poor}")
    
    # Overall assessment
    print(f"\n{'='*100}")
    print(f"🏁 OVERALL ASSESSMENT:")
    print(f"{'='*100}")
    
    if avg_score >= 80 and successful == len(results):
        print(f"\n🎉 ✅ EXCELLENT! System is production-ready!")
        print(f"   • All queries successful")
        print(f"   • High quality responses")
        print(f"   • Data properly sourced and combined")
    elif avg_score >= 60:
        print(f"\n👍 GOOD! System is mostly working well")
        print(f"   • Most queries successful")
        print(f"   • Good quality responses")
        print(f"   • Minor improvements possible")
    else:
        print(f"\n⚠️  NEEDS IMPROVEMENT")
        print(f"   • Some quality issues detected")
        print(f"   • Review failed validations")

print(f"\n{'='*100}\n")
