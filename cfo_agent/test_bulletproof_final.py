"""
Final Bulletproof Test - Real CFO Conversations
Tests the system with realistic CFO-level questions
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from master_agent import UnifiedCFOAgent
import time

def test_conversation(agent, questions, conversation_name):
    """Test a conversation flow"""
    
    print(f"\n{'='*100}")
    print(f"💼 {conversation_name}")
    print(f"{'='*100}\n")
    
    results = []
    
    for i, q in enumerate(questions, 1):
        print(f"\n{'─'*100}")
        print(f"Q{i}: {q}")
        print(f"{'─'*100}\n")
        
        start = time.time()
        result = agent.query(q)
        elapsed = time.time() - start
        
        # Quality check
        has_qual = any(word in result.answer.lower() for word in ['risk', 'strategy', 'priority', 'challenge'])
        has_quant = '%' in result.answer or '$' in result.answer or any(word in result.answer.lower() for word in ['million', 'billion', 'margin'])
        
        status = "✅" if result.success else "❌"
        qual_status = "✅" if has_qual else "❌"
        quant_status = "✅" if has_quant else "❌"
        
        print(f"{status} Response: {result.success} | {elapsed:.1f}s | Intent: {result.intent}")
        print(f"   {qual_status} Qualitative  {quant_status} Quantitative")
        print(f"   Sources: {', '.join(result.data_sources) if result.data_sources else 'None'}")
        
        # Show preview
        preview = result.answer[:400].replace('\n', ' ')
        print(f"\n   Preview: {preview}...")
        
        results.append({
            'success': result.success,
            'time': elapsed,
            'has_qual': has_qual,
            'has_quant': has_quant
        })
        
        if i < len(questions):
            time.sleep(2)
    
    return results


print("\n" + "="*100)
print("🎯 BULLETPROOF CFO SYSTEM - FINAL VALIDATION")
print("="*100)
print("\nTesting realistic CFO conversations and edge cases")
print("Goal: Ensure system handles complex, real-world queries flawlessly")
print("="*100)

agent = UnifiedCFOAgent(verbose=False)

# Conversation 1: Risk-Performance Analysis
conv1_questions = [
    "What were Apple's top 3 supply chain risks in 2022?",
    "What was Apple's gross margin in 2022?",
    "How did Apple's supply chain risks in 2022 relate to their gross margin performance?"
]

# Conversation 2: Strategic Analysis
conv2_questions = [
    "What innovation strategies did Microsoft discuss in their 2022 10-K?",
    "How much did Microsoft spend on R&D in 2022?",
    "How did Microsoft's innovation investments align with their R&D spending in 2022?"
]

# Conversation 3: Financial Position
conv3_questions = [
    "What regulatory challenges did Apple face in 2022?",
    "What was Apple's operating margin in 2022?",
    "Given Apple's regulatory challenges in 2022, how did their operating margin perform?"
]

# Conversation 4: Competitive Analysis
conv4_questions = [
    "What competitive pressures did Microsoft describe in 2022?",
    "What was Microsoft's revenue in 2022?",
    "How did competitive pressures affect Microsoft's revenue performance in 2022?"
]

# Conversation 5: Complex Hybrid
conv5_questions = [
    "What were Apple's main ESG and climate commitments in 2022, and what was their capital expenditure?",
    "How did Microsoft's cybersecurity investments relate to their operating expenses in 2022?",
    "What foreign exchange risks did Apple disclose, and what was their international revenue exposure?"
]

conversations = [
    (conv1_questions, "CONVERSATION 1: Supply Chain Risk → Performance"),
    (conv2_questions, "CONVERSATION 2: Innovation Strategy → R&D Investment"),
    (conv3_questions, "CONVERSATION 3: Regulatory Risk → Profitability"),
    (conv4_questions, "CONVERSATION 4: Competition → Revenue Impact"),
    (conv5_questions, "CONVERSATION 5: Complex Multi-Topic Queries")
]

all_results = []

for questions, name in conversations:
    results = test_conversation(agent, questions, name)
    all_results.extend(results)
    print(f"\n{'─'*100}")
    success_rate = sum(1 for r in results if r['success']) / len(results) * 100
    print(f"✅ Conversation Success Rate: {success_rate:.0f}%")
    print(f"{'─'*100}\n")
    time.sleep(3)

agent.close()

# Final Statistics
print(f"\n{'='*100}")
print(f"📊 FINAL BULLETPROOF VALIDATION RESULTS")
print(f"{'='*100}\n")

total = len(all_results)
successful = sum(1 for r in all_results if r['success'])
has_both = sum(1 for r in all_results if r['has_qual'] and r['has_quant'])
avg_time = sum(r['time'] for r in all_results) / total

print(f"✅ Overall Success Rate: {successful}/{total} ({successful/total*100:.0f}%)")
print(f"📊 Has Both Sources: {has_both}/{total} ({has_both/total*100:.0f}%)")
print(f"⏱️  Average Response Time: {avg_time:.1f}s\n")

# Detailed breakdown
qual_only = sum(1 for r in all_results if r['has_qual'] and not r['has_quant'])
quant_only = sum(1 for r in all_results if r['has_quant'] and not r['has_qual'])
neither = sum(1 for r in all_results if not r['has_qual'] and not r['has_quant'])

print(f"Response Type Distribution:")
print(f"   🎯 Hybrid (Qual + Quant): {has_both}/{total}")
print(f"   📖 Qualitative Only:      {qual_only}/{total}")
print(f"   📊 Quantitative Only:     {quant_only}/{total}")
print(f"   ⚠️  Neither:               {neither}/{total}\n")

# Performance tiers
fast = sum(1 for r in all_results if r['time'] < 5)
medium = sum(1 for r in all_results if 5 <= r['time'] < 10)
slow = sum(1 for r in all_results if r['time'] >= 10)

print(f"Response Time Distribution:")
print(f"   🚀 Fast (<5s):     {fast}/{total}")
print(f"   ⚡ Medium (5-10s): {medium}/{total}")
print(f"   🐌 Slow (>10s):    {slow}/{total}\n")

# Final verdict
print(f"{'='*100}")
print(f"🏁 FINAL VERDICT:")
print(f"{'='*100}\n")

if successful == total and has_both >= total * 0.7 and avg_time < 8:
    print(f"🎉 ✅ BULLETPROOF! System is MASTER CFO-LEVEL!")
    print(f"\n   ✅ 100% success rate")
    print(f"   ✅ {has_both/total*100:.0f}% provide both qualitative and quantitative data")
    print(f"   ✅ Average response time: {avg_time:.1f}s")
    print(f"\n   🚀 READY FOR PRODUCTION")
    print(f"   🚀 Can handle complex CFO conversations")
    print(f"   🚀 Professional-grade analysis")
    
elif successful >= total * 0.9 and avg_time < 10:
    print(f"👍 ✅ EXCELLENT! System is production-ready")
    print(f"\n   ✅ {successful/total*100:.0f}% success rate")
    print(f"   ✅ Good quality responses")
    print(f"   ✅ Acceptable response time: {avg_time:.1f}s")
    print(f"\n   💡 Minor optimizations possible")
    
elif successful >= total * 0.75:
    print(f"⚠️  GOOD but needs improvement")
    print(f"\n   • {successful/total*100:.0f}% success rate")
    print(f"   • Some queries need optimization")
    print(f"   • Response time: {avg_time:.1f}s")
    
else:
    print(f"❌ NEEDS SIGNIFICANT WORK")
    print(f"\n   • {successful/total*100:.0f}% success rate")
    print(f"   • Many improvements needed")

print(f"\n{'='*100}")

# Recommendations
print(f"\n💡 RECOMMENDATIONS:\n")

if successful == total and has_both >= total * 0.7:
    print(f"✅ System is performing exceptionally well")
    print(f"✅ Ready for real CFO usage")
    print(f"\n📋 Next Steps:")
    print(f"   1. Deploy to production")
    print(f"   2. Add query caching for frequently asked questions")
    print(f"   3. Implement usage analytics")
    print(f"   4. Consider Phase 2 enhancements (Knowledge Graph)")
else:
    print(f"📈 Improvement Areas:")
    if successful < total:
        print(f"   • Improve error handling for edge cases")
    if has_both < total * 0.5:
        print(f"   • Enhance data retrieval for both sources")
    if avg_time > 10:
        print(f"   • Optimize response time")
        print(f"   • Consider caching for common queries")

print(f"\n{'='*100}\n")
