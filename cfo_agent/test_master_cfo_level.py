"""
Master CFO-Level Testing Suite
Tests advanced hybrid queries that a real CFO would ask
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from master_agent import UnifiedCFOAgent
import time

def display_answer(question, result, test_num, total):
    """Display answer in a clean, readable format"""
    
    print(f"\n{'='*100}")
    print(f"📊 TEST {test_num}/{total}: MASTER CFO QUERY")
    print(f"{'='*100}\n")
    
    print(f"💼 CFO Question:")
    print(f"   \"{question}\"\n")
    
    print(f"⏱️  Response Time: {result.latency:.1f}s")
    print(f"🎯 Query Type: {result.intent.upper()}")
    print(f"📚 Data Sources: {', '.join(result.data_sources)}")
    print(f"✅ Success: {result.success}\n")
    
    if not result.success:
        print(f"❌ ERROR: {result.metadata.get('error', 'Unknown error')}\n")
        return
    
    print(f"{'─'*100}")
    print(f"📋 CFO ANALYSIS:")
    print(f"{'─'*100}\n")
    print(result.answer)
    print(f"\n{'─'*100}\n")
    
    # Quality assessment
    answer_lower = result.answer.lower()
    
    has_qualitative = any(word in answer_lower for word in ['risk', 'strategy', 'challenge', 'priority'])
    has_quantitative = '%' in result.answer or '$' in result.answer or any(word in answer_lower for word in ['million', 'billion'])
    has_structure = '##' in result.answer or 'QUALITATIVE' in result.answer
    has_insights = 'CFO Consideration' in result.answer or 'Financial Implications' in result.answer
    
    quality_score = sum([has_qualitative, has_quantitative, has_structure, has_insights]) * 25
    
    print(f"📊 Quality Assessment:")
    print(f"   {'✅' if has_qualitative else '❌'} Qualitative analysis")
    print(f"   {'✅' if has_quantitative else '❌'} Quantitative data")
    print(f"   {'✅' if has_structure else '❌'} Professional structure")
    print(f"   {'✅' if has_insights else '❌'} CFO-level insights")
    print(f"   Overall Score: {quality_score}%")
    
    if quality_score >= 75:
        print(f"   Grade: 🎉 EXCELLENT - Master CFO level")
    elif quality_score >= 50:
        print(f"   Grade: 👍 GOOD - Professional quality")
    else:
        print(f"   Grade: ⚠️  NEEDS IMPROVEMENT")
    
    return quality_score


# Advanced CFO-level test questions
print("\n" + "="*100)
print("🎯 MASTER CFO-LEVEL TESTING SUITE")
print("="*100)
print("\nTesting with advanced hybrid queries that real CFOs would ask...")
print("Focus: Complex analysis, multi-dimensional questions, strategic insights")
print("="*100)

agent = UnifiedCFOAgent(verbose=False)

# Master CFO-level questions covering different scenarios
test_questions = [
    {
        'category': 'Risk-Performance Correlation',
        'question': "How did Apple's cybersecurity threats in 2022 correlate with their R&D investments, and what does this tell us about their security posture?",
        'difficulty': 'Advanced',
        'expects': ['cybersecurity risks', 'R&D spending', 'correlation analysis']
    },
    {
        'category': 'Strategic-Financial Alignment',
        'question': "What were Microsoft's top 3 strategic priorities in 2022, and how did these align with their revenue distribution across segments?",
        'difficulty': 'Advanced',
        'expects': ['strategic priorities', 'revenue by segment', 'alignment analysis']
    },
    {
        'category': 'Operational Risk Impact',
        'question': "What supply chain disruptions did Apple disclose in their 2022 10-K, and what was the actual impact on their gross margin compared to prior year?",
        'difficulty': 'Expert',
        'expects': ['supply chain risks', 'gross margin', 'year-over-year comparison']
    },
    {
        'category': 'Competitive Position Analysis',
        'question': "How did Microsoft describe competitive threats from cloud providers in 2022, and what was their cloud revenue growth rate?",
        'difficulty': 'Advanced',
        'expects': ['competitive threats', 'cloud revenue', 'growth rate']
    },
    {
        'category': 'Regulatory Risk-Financial Resilience',
        'question': "What regulatory challenges did Apple face in 2022, particularly around App Store policies, and how did their operating cash flow demonstrate resilience?",
        'difficulty': 'Expert',
        'expects': ['regulatory risks', 'App Store', 'operating cash flow']
    },
    {
        'category': 'Innovation Investment ROI',
        'question': "What innovation initiatives did Apple highlight in 2022, how much did they spend on R&D, and what was their gross profit that year?",
        'difficulty': 'Advanced',
        'expects': ['innovation strategy', 'R&D spending', 'gross profit']
    },
    {
        'category': 'Market Risk-Revenue Impact',
        'question': "What foreign exchange risks did Apple disclose for 2022, and what was their actual international revenue exposure?",
        'difficulty': 'Expert',
        'expects': ['FX risks', 'international revenue', 'currency exposure']
    },
    {
        'category': 'Crisis Management-Financial Position',
        'question': "How did Apple address COVID-19 impacts in their 2022 disclosures, and what was their cash position and liquidity ratio?",
        'difficulty': 'Advanced',
        'expects': ['COVID-19 risks', 'cash position', 'liquidity metrics']
    },
    {
        'category': 'ESG-Operational Efficiency',
        'question': "What environmental and sustainability commitments did Microsoft make in 2022, and how did their operating expenses trend?",
        'difficulty': 'Advanced',
        'expects': ['ESG commitments', 'operating expenses', 'efficiency trends']
    },
    {
        'category': 'Comparative Analysis',
        'question': "Compare the regulatory risks Apple and Microsoft faced in 2022, and which company had higher operating margins?",
        'difficulty': 'Expert',
        'expects': ['Apple risks', 'Microsoft risks', 'comparative margins']
    }
]

results = []
total_tests = len(test_questions)

for i, test in enumerate(test_questions, 1):
    print(f"\n{'='*100}")
    print(f"Category: {test['category']}")
    print(f"Difficulty: {test['difficulty']}")
    print(f"Expected elements: {', '.join(test['expects'])}")
    print(f"{'='*100}")
    
    result = agent.query(test['question'])
    score = display_answer(test['question'], result, i, total_tests)
    
    results.append({
        'category': test['category'],
        'difficulty': test['difficulty'],
        'success': result.success,
        'score': score if result.success else 0,
        'latency': result.latency,
        'sources': result.data_sources
    })
    
    if i < total_tests:
        wait_time = 3
        print(f"\n⏳ Waiting {wait_time} seconds before next test...")
        time.sleep(wait_time)

agent.close()

# Final Analysis
print(f"\n{'='*100}")
print(f"📊 MASTER CFO-LEVEL TEST RESULTS")
print(f"{'='*100}\n")

successful = [r for r in results if r['success']]
success_rate = len(successful) / len(results) * 100

avg_score = sum(r['score'] for r in successful) / len(successful) if successful else 0
avg_latency = sum(r['latency'] for r in successful) / len(successful) if successful else 0

print(f"✅ Success Rate: {len(successful)}/{len(results)} ({success_rate:.0f}%)")
print(f"📊 Average Quality Score: {avg_score:.0f}%")
print(f"⏱️  Average Response Time: {avg_latency:.1f}s\n")

# Score distribution
excellent = sum(1 for r in results if r['score'] >= 75)
good = sum(1 for r in results if 50 <= r['score'] < 75)
poor = sum(1 for r in results if r['score'] < 50)

print(f"Grade Distribution:")
print(f"   🎉 Excellent (75-100%):  {excellent}/{len(results)}")
print(f"   👍 Good (50-74%):       {good}/{len(results)}")
print(f"   ⚠️  Poor (<50%):         {poor}/{len(results)}\n")

# Difficulty analysis
print(f"Performance by Difficulty:")
advanced_tests = [r for r in results if r['difficulty'] == 'Advanced']
expert_tests = [r for r in results if r['difficulty'] == 'Expert']

if advanced_tests:
    adv_success = sum(1 for r in advanced_tests if r['success']) / len(advanced_tests) * 100
    adv_avg_score = sum(r['score'] for r in advanced_tests if r['success']) / sum(1 for r in advanced_tests if r['success']) if any(r['success'] for r in advanced_tests) else 0
    print(f"   Advanced: {adv_success:.0f}% success, {adv_avg_score:.0f}% avg quality")

if expert_tests:
    exp_success = sum(1 for r in expert_tests if r['success']) / len(expert_tests) * 100
    exp_avg_score = sum(r['score'] for r in expert_tests if r['success']) / sum(1 for r in expert_tests if r['success']) if any(r['success'] for r in expert_tests) else 0
    print(f"   Expert:   {exp_success:.0f}% success, {exp_avg_score:.0f}% avg quality\n")

# Final verdict
print(f"{'='*100}")
print(f"🏁 FINAL VERDICT:")
print(f"{'='*100}\n")

if success_rate == 100 and avg_score >= 75:
    print(f"🎉 ✅ BULLETPROOF! Master CFO-level system")
    print(f"   • All queries handled successfully")
    print(f"   • Excellent quality across the board")
    print(f"   • Ready for production deployment")
    print(f"   • Can handle complex, multi-dimensional CFO queries")
elif success_rate >= 80 and avg_score >= 60:
    print(f"👍 STRONG! Professional-grade system")
    print(f"   • Most queries handled well")
    print(f"   • Good quality responses")
    print(f"   • Minor improvements possible")
elif success_rate >= 60:
    print(f"⚠️  ADEQUATE but needs improvement")
    print(f"   • Some queries struggling")
    print(f"   • Quality could be better")
    print(f"   • Requires optimization")
else:
    print(f"❌ NEEDS SIGNIFICANT WORK")
    print(f"   • Many failures detected")
    print(f"   • Quality issues present")
    print(f"   • Major improvements required")

print(f"\n{'='*100}\n")

# Recommendations
print(f"💡 RECOMMENDATIONS:\n")

if avg_score >= 75:
    print(f"✅ System is performing at master CFO level")
    print(f"✅ Ready for production use with complex queries")
    print(f"✅ Consider adding query caching for performance")
else:
    print(f"📈 Areas for improvement:")
    if avg_score < 75:
        print(f"   • Enhance synthesis quality")
        print(f"   • Improve CFO-level insights")
        print(f"   • Add more contextual analysis")
    if avg_latency > 10:
        print(f"   • Optimize response time (current: {avg_latency:.1f}s)")
        print(f"   • Consider caching frequently asked queries")

print(f"\n{'='*100}\n")
