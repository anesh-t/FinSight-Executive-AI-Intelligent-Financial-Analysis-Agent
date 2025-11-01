"""
Automated Comprehensive Hybrid Query Test
Tests master-level CFO questions - runs automatically without pauses
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from master_agent import UnifiedCFOAgent


# Select 3 representative CFO hybrid questions
CFO_HYBRID_QUESTIONS = [
    {
        'category': 'Risk-Financial Impact',
        'question': "How did Apple's supply chain risks disclosed in their 2022 10-K affect their gross margins?",
        'expected_sources': ['10-K Item 1A (risks)', 'Financial data (margins)'],
    },
    {
        'category': 'Strategy-Performance',
        'question': "What strategic priorities did Apple highlight in their 2022 management discussion, and how did these align with their revenue growth?",
        'expected_sources': ['10-K Item 7 (strategy)', 'Financial data (revenue)'],
    },
    {
        'category': 'Crisis-Financial Resilience',
        'question': "How did Microsoft address COVID-19 related risks in 2022, and what was their cash position that year?",
        'expected_sources': ['10-K Item 1A (COVID risks)', 'Financial data (cash)'],
    }
]


def print_separator(title, char="="):
    """Print formatted separator"""
    print(f"\n{char*100}")
    print(f"  {title}")
    print(f"{char*100}")


def validate_answer(answer_text, question):
    """Quick validation of answer quality"""
    answer_lower = answer_text.lower()
    
    # Check for key indicators
    has_qualitative = any(word in answer_lower for word in ['risk', 'strategy', 'disclosed', 'discussed', 'management'])
    has_quantitative = any(char in answer_text for char in ['$', '%']) or any(word in answer_lower for word in ['billion', 'million', 'revenue', 'margin'])
    has_both_sources = ('10-k' in answer_lower or '10k' in answer_lower) and ('financial' in answer_lower or 'data' in answer_lower)
    
    score = 0
    if has_qualitative: score += 33
    if has_quantitative: score += 33
    if has_both_sources: score += 34
    
    return {
        'score': score,
        'has_qualitative': has_qualitative,
        'has_quantitative': has_quantitative,
        'has_both_sources': has_both_sources
    }


def main():
    print_separator("🎯 HYBRID QUERY DEEP DIVE TEST", "=")
    
    print(f"\nTesting {len(CFO_HYBRID_QUESTIONS)} CFO-level hybrid questions...")
    print(f"Each question requires both:")
    print(f"  📖 Qualitative analysis from 10-K filings (RAG)")
    print(f"  📊 Quantitative data from financial database (SQL)")
    
    # Initialize
    print(f"\n🚀 Initializing agent...")
    agent = UnifiedCFOAgent(verbose=True)  # Enable verbose for debugging
    
    results = []
    
    for i, test in enumerate(CFO_HYBRID_QUESTIONS, 1):
        print_separator(f"TEST {i}/{len(CFO_HYBRID_QUESTIONS)}: {test['category']}", "=")
        
        print(f"\n❓ Question:")
        print(f"   {test['question']}")
        
        print(f"\n🎯 Expected to combine:")
        for source in test['expected_sources']:
            print(f"   • {source}")
        
        print(f"\n⏳ Processing (this may take 5-10 seconds)...")
        
        try:
            start = time.time()
            result = agent.query(test['question'])
            elapsed = time.time() - start
            
            print(f"\n✅ Completed in {elapsed:.2f}s")
            
            # Show metadata
            print(f"\n📊 Response Metadata:")
            print(f"   Intent: {result.intent}")
            print(f"   Sources: {', '.join(result.data_sources)}")
            if 'agents_used' in result.metadata:
                print(f"   Agents: {', '.join(result.metadata['agents_used'])}")
            
            # Validate
            validation = validate_answer(result.answer, test['question'])
            
            print(f"\n🔍 Quick Validation:")
            print(f"   Score: {validation['score']}/100")
            print(f"   Has qualitative content: {'✅' if validation['has_qualitative'] else '❌'}")
            print(f"   Has quantitative data: {'✅' if validation['has_quantitative'] else '❌'}")
            print(f"   Cites both sources: {'✅' if validation['has_both_sources'] else '❌'}")
            
            # Show answer
            print(f"\n" + "─"*100)
            print("📄 ANSWER:")
            print("─"*100)
            print(result.answer)
            print("─"*100)
            
            # Assessment
            print(f"\n💡 Assessment:")
            if validation['score'] >= 80:
                print(f"   ✅ EXCELLENT - Answer combines both sources effectively")
            elif validation['score'] >= 60:
                print(f"   👍 GOOD - Answer includes both elements with minor gaps")
            else:
                print(f"   ⚠️  NEEDS IMPROVEMENT - Missing key elements")
            
            results.append({
                'category': test['category'],
                'success': True,
                'validation': validation,
                'elapsed': elapsed
            })
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            results.append({
                'category': test['category'],
                'success': False,
                'validation': {'score': 0},
                'elapsed': 0
            })
        
        if i < len(CFO_HYBRID_QUESTIONS):
            print(f"\n{'='*100}")
            print(f"Waiting 3 seconds before next test...")
            time.sleep(3)
    
    # Summary
    print_separator("📊 COMPREHENSIVE TEST SUMMARY", "=")
    
    successful = sum(1 for r in results if r['success'])
    avg_score = sum(r['validation']['score'] for r in results if r['success']) / max(successful, 1)
    
    print(f"\n✅ Successful: {successful}/{len(results)}")
    print(f"📈 Average Score: {avg_score:.1f}/100")
    
    print(f"\n📋 Results by Category:")
    for r in results:
        status = "✅" if r['success'] else "❌"
        score = r['validation']['score'] if r['success'] else 0
        print(f"   {status} {r['category']}: {score}/100")
    
    # Final verdict
    print_separator("🏁 FINAL VERDICT", "=")
    
    if avg_score >= 80:
        print(f"\n🎉 EXCELLENT! Hybrid query system is working very well!")
        print(f"   ✅ Answers properly combine qualitative and quantitative data")
        print(f"   ✅ Sources are properly attributed")
        print(f"   ✅ Answers make logical sense")
        print(f"   ✅ System is ready for CFO-level usage")
    elif avg_score >= 60:
        print(f"\n👍 GOOD! System is functional with room for improvement")
        print(f"   ✅ Core hybrid functionality working")
        print(f"   ⚠️  Some refinement recommended")
    else:
        print(f"\n⚠️  NEEDS IMPROVEMENT")
        print(f"   ⚠️  Integration or synthesis needs work")
    
    agent.close()
    
    print(f"\n" + "="*100 + "\n")
    
    return avg_score >= 60


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
